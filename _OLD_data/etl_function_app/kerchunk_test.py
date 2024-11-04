import kerchunk.hdf
import fsspec

fs = fsspec.filesystem(
    protocol="az",
    account_name="saenigmaarchivedev",
    anon=False,
)

urls = list(fs.glob("analysis/uch/nwp2/*/*/*.nc"))

url = urls[0]

import kerchunk.netCDF3

singles = []
for url in urls[:3]:
    with fs.open(url) as f:
        chunks = kerchunk.netCDF3.NetCDF3ToZarr(f"az://{url}", storage_options=fs.storage_options, inline_threshold=0, version=2)
        singles.append(chunks.translate())
    print("Done:", url)

from kerchunk.combine import MultiZarrToZarr

mzz = MultiZarrToZarr(
    singles,
    remote_protocol="az",
    remote_options=fs.storage_options,
    concat_dims=["time_utc", "calculation_time_utc"],
    identical_dims=["latitude", "longitude"],
    cons
)

out = mzz.translate()