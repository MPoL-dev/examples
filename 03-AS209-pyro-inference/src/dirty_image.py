import numpy as np
import asdf
import matplotlib
import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker

from mpol import coordinates, gridding

from common import make_dirty_image

def plot_dirty_image():

    img, beam = make_dirty_image(np.real(data), np.imag(data))

    # set plot dimensions
    xx = 8 # in
    cax_width = 0.2 # in 
    cax_sep = 0.1 # in
    mmargin = 1.2
    lmargin = 0.7
    rmargin = 0.7
    tmargin = 0.3
    bmargin = 0.5

    npanels = 2
    # the size of image axes + cax_sep + cax_width
    block_width = (xx - lmargin - rmargin - mmargin * (npanels - 1) )/npanels
    ax_width = block_width - cax_width - cax_sep
    ax_height = ax_width 
    yy = bmargin + ax_height + tmargin

    fig = plt.figure(figsize=(xx, yy))
    ax = []
    cax = []
    for i in range(npanels):
        ax.append(fig.add_axes([(lmargin + i * (block_width + mmargin))/xx, bmargin/yy, ax_width/xx, ax_height/yy]))
        cax.append(fig.add_axes([(lmargin + i * (block_width + mmargin) + ax_width + cax_sep)/xx, bmargin/yy, cax_width/xx, ax_height/yy]))

    # single-channel image cube    
    chan = 0

    im_beam = ax[0].imshow(beam[chan], **kw)
    cbar = plt.colorbar(im_beam, cax=cax[0])
    ax[0].set_title("beam")
    # zoom in a bit
    r = 0.3
    ax[0].set_xlim(r, -r)
    ax[0].set_ylim(-r, r)

    im = ax[1].imshow(img[chan], **kw)
    ax[1].set_title("dirty image")
    cbar = plt.colorbar(im, cax=cax[1])
    cbar.set_label(r"Jy/$\mathrm{arcsec}^2$")

    for a in ax:
        a.set_xlabel(r"$\Delta \alpha \cos \delta$ [${}^{\prime\prime}$]")
        a.set_ylabel(r"$\Delta \delta$ [${}^{\prime\prime}$]")

def main():
    

    # load extracted visibilities from asdf file
    d = asdf.open(fname)
    uu = d["uu"]
    vv = d["vv"]
    weight = d["weight"]
    data = d["data"]
