from datasets import load_dataset
from PIL import Image, ImageOps, ImageMath
import numpy as np
import matplotlib.pyplot as plt
import argparse

dataset = load_dataset("ceyda/smithsonian_butterflies")


def save_list(ids):
    for id in ids:
        dataset["train"][id]["image"].save("plots/{:}.png".format(id))


def process_image(
    pil_image, npix, cell_size, total_flux, right_crop=0, centerfrac=0.8, scale=0.1
):
    """
    Run the pipeline to apply transformations to the image and turn it into a numpy array.

    right_crop: crop these number of pixels from the right
    """

    im_grey = ImageOps.grayscale(pil_image)
    xsize, ysize = im_grey.size

    # we usually have a darker butterfly on a white background
    # so we'll invert
    im_invert = ImageOps.invert(im_grey)

    # we may need to crop scale bar. Let's just leave it for now and see what happens
    if right_crop > 0:
        im_invert = im_invert.crop((0, 0, xsize - right_crop, ysize))
        # im_invert.show()

    # apodize
    im_apod = apodization_function(xsize, ysize, centerfrac, scale)
    im_res = ImageMath.lambda_eval(lambda d: d["a"] * d["b"], a=im_invert, b=im_apod)

    # pad to square
    max_dim = np.maximum(xsize, ysize)
    im_pad = ImageOps.pad(im_res, (max_dim, max_dim))

    # resize to 1028, 1028.
    assert max_dim > npix, "Image {:} smaller than npix {:}".format(max_dim, npix)
    im_small = im_pad.resize((npix, npix))

    # convert from PIL to im
    a = np.array(im_small)

    # resizing operation can create some negative pixels, so
    # best to just set these to the minimum, which should be 0
    a[a < 0] = 0.0

    b = a.astype("float64")
    # norm to 1
    b = b / b.max()

    # upright
    c = np.flipud(b)

    pixel_area = cell_size**2  # arcsec

    # scale to correct total flux
    old_flux = np.sum(c * pixel_area)
    flux_scaled = total_flux / old_flux * c

    return flux_scaled


def logistic_taper(N, centerfrac=0.8, scale=0.1):
    "Larger scale values increases speed of taper."
    assert N % 2 == 0, "Image must have even number of pixels."
    xs = np.arange(N)
    x1 = N * (1 - centerfrac) / 2
    x2 = N - x1

    y1 = 1 / (1 + np.exp(-scale * (xs[: N // 2] - x1)))
    y2 = 1 - 1 / (1 + np.exp(-scale * (xs[N // 2 :] - x2)))
    return np.concatenate([y1, y2])


def apodization_function(xsize, ysize, centerfrac=0.8, scale=0.1):
    """
    Create a function of this size that can be multiplied against another to taper edges.
    """

    xtaper = logistic_taper(xsize, centerfrac=centerfrac, scale=scale)
    ytaper = logistic_taper(ysize, centerfrac=centerfrac, scale=scale)

    taper = np.outer(ytaper, xtaper)

    # now convert the numpy array to a Pillow object
    # scale to 0 - 255 and then convert to uint8
    taper8 = np.uint8(taper * 255)
    return Image.fromarray(taper8)


def main():
    parser = argparse.ArgumentParser(
        description="""Create a mock image."""
    )
    parser.add_argument("outfile", help="Output file")
    parser.add_argument("plot_file")
    args = parser.parse_args()

    # DSHARP says F_nu is 0.253 Jy
    npix = 1028
    cell_size = 0.005
    arr = process_image(
        dataset["train"][182]["image"],
        npix,
        cell_size,
        0.253,
        right_crop=200,
        centerfrac=0.9,
        scale=0.2,
    )

    # save this to .npy for future reference
    arr = arr.astype(np.float32)
    np.save(args.outfile, arr)

    # plot the image
    fig, ax = plt.subplots(nrows=1)
    im = ax.imshow(arr, origin="lower", cmap='inferno')
    plt.colorbar(im, ax=ax)
    fig.savefig(args.plot_file, dpi=300)


if __name__ == "__main__":
    main()
