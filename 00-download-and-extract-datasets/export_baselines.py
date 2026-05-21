import numpy as np
from casatools import msmetadata
from visread import process_casa
import matplotlib.pyplot as plt
import argparse


def get_mock_baselines(ms, select_fraction=0.1):
    weight_list = []
    uu_list = []
    vv_list = []

    msmd = msmetadata()
    msmd.open(ms)
    ddids = msmd.datadescids()
    msmd.close()

    # for a given spw
    for ddid in ddids:
        # get processed visibilities
        # includes flipping frequency, if necessary
        # including complex conjugation
        # no channel-averaging (assuming DSHARP did this to the maximal extent possible)
        d = process_casa.get_processed_visibilities(ms, ddid)

        # True if flagged
        flag = d["flag"]

        # compress over channel
        flag = np.any(flag, axis=0)

        uu = d["uu"][~flag]  # keep the good ones
        vv = d["vv"][~flag]

        # weight is always 1D
        # apply flags, in case weights are wonky
        weight = d["weight"][~flag]

        # destroy channel axis and concatenate
        uu_list.append(uu.flatten())
        vv_list.append(vv.flatten())
        weight_list.append(weight.flatten())

    # concatenate all files at the end
    uu = np.concatenate(uu_list)
    vv = np.concatenate(vv_list)
    weight = np.concatenate(weight_list)

    # select inds
    index = np.arange(len(uu))
    rng = np.random.default_rng(seed=42)
    ind = rng.choice(index, size=int(select_fraction * len(uu)))

    return uu[ind], vv[ind], weight[ind]


def main():
    parser = argparse.ArgumentParser(
        description="""Take visibilities in the measurement set and extract the relevant 
        uu, vv, and weight values."""
    )
    parser.add_argument("ms", help="Filename of measurement set")
    parser.add_argument("outfile", help="Output file")
    parser.add_argument("plot_file")
    parser.add_argument(
        "--select_fraction", type=float, help="Fraction to select.", default=1.0
    )
    args = parser.parse_args()

    uu, vv, weight = get_mock_baselines(args.ms, args.select_fraction)

    plt.scatter(uu, vv, 0.5)
    plt.savefig(args.plot_file, dpi=300)

    np.savez(
        args.outfile,
        uu=uu.astype(np.float32),
        vv=vv.astype(np.float32),
        weight=weight.astype(np.float32),
    )

if __name__ == "__main__":
    main()
