import torch
import argparse
import matplotlib.pyplot as plt
from mpol import coordinates, images
from mpol.constants import arcsec
from astropy.visualization.mpl_normalize import simple_norm

def main():
    parser = argparse.ArgumentParser(description="Compare image to DSHARP image")
    parser.add_argument("load_checkpoint", metavar="load-checkpoint", help="Path to checkpoint from which to resume.")
    parser.add_argument("plotfile")
    args = parser.parse_args()

    # get the MPoL image from the checkpoint
    coords = coordinates.GridCoords(cell_size=0.005, npix=1028)
    checkpoint = torch.load(args.load_checkpoint, map_location=torch.device('cpu'))

    # get the image cube in packed format and run through an ImageCube to unpack
    icube = images.ImageCube(coords=coords)
    icube(checkpoint["model_state_dict"]["icube.packed_cube"])

    # remove channel dimension
    mpol_img = torch.squeeze(icube.sky_cube)
   
    lmargin = 1.0
    rmargin = lmargin
    XX = 5. #in 
    ax_width = (XX - lmargin - rmargin)
    ax_height = ax_width

    cax_sep = 0.05
    cax_width = 0.1
    tmargin = 0.05
    bmargin = 1.0
    YY = bmargin + ax_height + tmargin

    fig = plt.figure(figsize=(XX,YY))

    ax = fig.add_axes((lmargin/XX, bmargin/YY, ax_width/XX, ax_height/YY))
    cax = fig.add_axes(((lmargin + ax_width + cax_sep)/XX, bmargin/YY, cax_width/XX, ax_height/YY))
   
    im = ax.imshow(mpol_img, extent=coords.img_ext, origin="lower", cmap="inferno")
    cbar = plt.colorbar(im, cax=cax)
    cbar.ax.tick_params(labelsize=9) 
    cbar.set_label(r"Jy/arcsec$^2$")

    ax.set_xlabel(r"$\Delta \alpha \cos \delta$ [${}^{\prime\prime}$]")
    ax.set_ylabel(r"$\Delta \delta$ [${}^{\prime\prime}$]")

    fig.subplots_adjust(wspace=0.25)
    fig.savefig(args.plotfile, dpi=300)


if __name__ == "__main__":
    main()