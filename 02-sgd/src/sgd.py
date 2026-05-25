import numpy as np
import load_data
import dirty_image
import torch
import argparse
import matplotlib.colors as mco
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from mpol import coordinates, gridding, fourier, images, losses, utils, plot

from torch.utils.tensorboard import SummaryWriter

# for validation calculation
mle = torch.nn.MSELoss()
        
# create the forward model
class Net(torch.nn.Module):
    def __init__(
        self,
        coords=None,
        nchan=1,
        FWHM=0.05
    ):
        super().__init__()
        self.coords = coords
        self.nchan = nchan

        self.bcube = images.BaseCube(coords=self.coords, nchan=self.nchan)
        self.conv_layer = images.GaussConvFourier(coords=self.coords, FWHM_maj=FWHM, FWHM_min=FWHM)
        self.icube = images.ImageCube(coords=self.coords, nchan=self.nchan)
        self.nufft = fourier.NuFFT(coords=self.coords, nchan=self.nchan)

    def forward(self, uu, vv):
        r"""
        Predict model visibilities at baseline locations.

        Parameters
        ----------
        uu, vv : torch.Tensor
            spatial frequencies. Units of :math:`\lambda`.

        Returns
        -------
        torch.Tensor
            1D complex torch tensor of model visibilities.
        """
        # Feed-forward network passes base representation through "layers"
        # to create model visibilities
        x = self.bcube()
        x = self.conv_layer(x)
        x = self.icube(x)
        vis = self.nufft(x, uu, vv)
        return vis

# pre-calculate the quantities needed to plot the power spectrum
# get max baseline
q_data = torch.hypot(load_data.vis_data.uu, load_data.vis_data.vv)
q_max = torch.max(q_data)

# use pre-defined variables in load_data
flayer = fourier.FourierCube(load_data.coords)
# pass through layer to set internal state
flayer(load_data.packed_cube)

# get the amp vs. qs for the true image
true_amp = utils.torch2npy(flayer.ground_amp.flatten())
qs = load_data.coords.ground_q_centers_2D.flatten()


def plots(model, step, writer):
    """
    Plot images to the Tensorboard instance.
    """

    img = np.squeeze(utils.torch2npy(model.icube.sky_cube))
    fig, ax = plt.subplots(nrows=1)
    plot.plot_image(img, extent=model.coords.img_ext, ax=ax)
    writer.add_figure("image", fig, step)

    # compare power spectra
    fig, ax = plt.subplots(nrows=1)
    ax.axvline(q_max * 1e-6, lw=0.5, zorder=-1)
    ax.scatter(qs *1e-6, true_amp, s=0.4, rasterized=True, linewidths=0.0, c="k", alpha=0.2, label="true")
    flayer(model.icube.packed_cube)
    model_amp = utils.torch2npy(flayer.ground_amp.flatten())
    ax.scatter(qs *1e-6, model_amp, s=0.4, rasterized=True, linewidths=0.0, c="C0", alpha=0.2, label="model")
    ax.set_xlabel(r"$q$ [M$\lambda$]")
    ax.set_ylabel(r"$|V|$ [Jy]")
    ax.set_yscale("log")
    writer.add_figure("spectrum", fig, step)

    bcube = np.squeeze(
        utils.torch2npy(utils.packed_cube_to_sky_cube(model.bcube.base_cube))
    )
    norm = mco.Normalize(vmin=np.min(bcube), vmax=np.max(bcube))
    fig, ax = plt.subplots(nrows=1)
    plot.plot_image(bcube, extent=model.coords.img_ext, ax=ax, norm=norm)
    writer.add_figure("bcube", fig, step)

    # get gradient as it exists on model from root node
    b_grad = np.squeeze(
        utils.torch2npy(utils.packed_cube_to_sky_cube(model.bcube.base_cube.grad))
    )
    norm_sym = plot.get_image_cmap_norm(b_grad, symmetric=True)
    fig, ax = plt.subplots(nrows=1)
    plot.plot_image(
        b_grad, extent=model.coords.img_ext, norm=norm_sym, ax=ax, cmap="bwr_r"
    )
    writer.add_figure("b_grad", fig, step)


def residual_dirty_image(coords, model_vis, uu, vv, data, weight, step, writer):
    # calculate residual dirty image for this *batch*
    resid = data - model_vis
    imager = gridding.DirtyImager.from_tensors(
        coords=coords, uu=uu, vv=vv, weight=weight, data=resid
    )
    img, beam = imager.get_dirty_image(
        weighting="briggs",
        robust=0.0,
        check_visibility_scatter=False,
        unit="Jy/arcsec^2",
    )

    fig = dirty_image.plot_beam_and_image(beam, img, imager.coords.img_ext)
    writer.add_figure("dirty_image", fig, step)


def train(args, model, device, train_loader, optimizer, epoch, lam_ent, writer):
    model.train()
    for i_batch, (uu, vv, weight, data) in enumerate(train_loader):
        # send all values to device
        uu, vv, weight, data = (
            uu.to(device),
            vv.to(device),
            weight.to(device),
            data.to(device),
        )

        optimizer.zero_grad()
        # get model visibilities
        vis = model(uu, vv)[0]  # take only the first channel

        # calculate loss
        loss = losses.neg_log_likelihood_avg(
            vis, data, weight
        ) + lam_ent * losses.entropy(
            model.icube.packed_cube, prior_intensity=1e-4, tot_flux=0.253
        )
        loss.backward()
        optimizer.step()

        # log results
        if i_batch % args.log_interval == 0:
            print(
                "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                    epoch,
                    i_batch * len(data),
                    len(train_loader.dataset),
                    100.0 * i_batch / len(train_loader),
                    loss.item(),
                )
            )

            step = i_batch + epoch * len(train_loader)
            writer.add_scalar("loss", loss.item(), step)
            plots(model, step, writer)
            residual_dirty_image(model.coords, vis, uu, vv, data, weight, step, writer)
            if args.dry_run:
                break



def validate(model, device):
    model.eval()
    ref_cube = load_data.sky_cube.to(device)

    FWHMs = [0.02, 0.06, 0.1] # arcsec
    loss_dict = {}
    loss_dict["raw"] = mle(model.icube.sky_cube, ref_cube)
    # speed up calculation by disabling gradients
    with torch.no_grad():
        # convolve packed cubes to common resolution
        for FWHM in FWHMs:
            layer = images.GaussConvFourier(model.coords, FWHM_maj=FWHM, FWHM_min=FWHM).to(device)
            ref_cube_convolved = layer(ref_cube)
            model_cube_convolved = layer(model.icube.sky_cube)
            loss_dict["FWHM: {:.2f}".format(FWHM)] = mle(model_cube_convolved, ref_cube_convolved)

    return loss_dict

def main():
    # Training settings
    parser = argparse.ArgumentParser(description="IM Lup SGD Example")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2000,
        help="input batch size for training",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="number of epochs to train",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=1e-3,
        help="learning rate",
    )
    parser.add_argument("--FWHM", type=float, default=0.05, help="FWHM of Gaussian Base layer in arcseconds.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="quickly check a single pass",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=4,
        help="how many batches to wait before logging training status",
    )
    parser.add_argument(
        "--tensorboard-log-dir",
        help="The log dir to which tensorboard files should be written.",
    )
    parser.add_argument("--lam-ent", type=float, default=0.0)
    parser.add_argument(
        "--load-checkpoint", help="Path to checkpoint from which to resume."
    )
    parser.add_argument(
        "--save-checkpoint",
        help="Path to which checkpoint where finished model and optimizer state should be saved.",
    )
    args = parser.parse_args()

    # set seed
    torch.manual_seed(42)

    # choose the compute device, preference cuda > mps > cpu
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")


    # load the dataset
    vis_data = load_data.vis_data

    # TensorDataset can be indexed just like a numpy array.
    train_dataset = TensorDataset(
        vis_data.uu, vis_data.vv, vis_data.weight, vis_data.data
    )

    print("running on ", device)
    print("total vis", len(train_dataset))

    # set the batch sizes for the loaders
    if torch.cuda.is_available():
        cuda_kwargs = {"num_workers": 1, "pin_memory": True}
    else:
        cuda_kwargs = {}

    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True, **cuda_kwargs
    )

    # create the model and send to device
    coords = coordinates.GridCoords(cell_size=0.005, npix=1028)
    model = Net(coords, nchan=1, FWHM=args.FWHM).to(device)

    # create optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    if args.load_checkpoint is not None:
        checkpoint = torch.load(args.load_checkpoint)
        model.load_state_dict(checkpoint["model_state_dict"], strict=False)

    # set up TensorBoard instance
    writer = SummaryWriter(log_dir=args.tensorboard_log_dir)

    # enter the loop
    for epoch in range(0, args.epochs):
        train(args, model, device, train_loader, optimizer, epoch, args.lam_ent, writer)
        vloss_dict = validate(model, device)
        writer.add_scalars("vloss", vloss_dict, epoch)
        optimizer.step()

    # save checkpoint
    if args.save_checkpoint is not None:
        torch.save(
            {
                "model_state_dict": model.state_dict(),
            },
            args.save_checkpoint,
        )

    writer.close()


if __name__ == "__main__":
    main()
