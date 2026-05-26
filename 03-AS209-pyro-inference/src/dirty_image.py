import numpy as np
import asdf
import matplotlib
import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker

from mpol import coordinates, gridding

# settle on an image size that we'll use throughout the tutorial
coords = coordinates.GridCoords(cell_size=0.005, npix=800)
kw = {"origin": "lower", "interpolation": "none", "extent": coords.img_ext, "cmap":"inferno"}


def make_dirty_image(data_real, data_imag, robust=-0.5):
    """
    Make a plot of the dirty beam and dirty image (in units of Jy/arcsec^2).
    
    Args:
        data_real (numpy array): real components of visibilities
        data_imag (numpy array): imaginary components of visibilities
        robust (float): the Briggs robust parameter
        
    Returns:
        beam, image numpy arrays
    """

    imager = gridding.DirtyImager(
        coords=coords,
        uu=uu,
        vv=vv,
        weight=weight,
        data_re=data_real,
        data_im=data_imag,
    )

    return imager.get_dirty_image(weighting="briggs", robust=robust, unit="Jy/arcsec^2")




# load extracted visibilities from asdf file 
d = asdf.open(fname)
uu = d["uu"]
vv = d["vv"]
weight = d["weight"]
data = d["data"]    



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
