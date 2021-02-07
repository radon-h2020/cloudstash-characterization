import sys
import os
import seaborn
import pandas
from argparse import ArgumentParser


# Create the cli parser
cli_args_parser = ArgumentParser(
    description="Draw plots based on output from the sequential benchmark",
    epilog="By @zanderhavgaard & @ChristofferNissen for the Radon H2020 Project",
)

# define the cli arguments
cli_args_parser.add_argument(
    "csv_file",
    type=str,
    help="Which csv file to draw plots from",
)
cli_args_parser.add_argument(
    "--output_path",
    type=str,
    default=".",
    help="Path to where to write plots, defaults to current directory",
)
cli_args_parser.add_argument(
    "--only_print_data",
    action="store_true",
    help="Will print data as pandas dataframe for previewing that data is loaded correctly",
)

# parse the cli arguments
cli_args = cli_args_parser.parse_args()

# load cli args into variables
csv_file = cli_args.csv_file
plots_path = cli_args.output_path
only_print_data = cli_args.only_print_data

if not os.path.isfile(csv_file):
    print(f"Error: The file {csv_file} could not be found")
    sys.exit(1)

#  csv_file = "../output/0ebbd90c-sequential_upload-200.csv"
print(f"Using .csv file {csv_file}")

print("Reading data ...")
# read .csv file to pandas dataframe
sequential_data = pandas.read_csv(csv_file)

if only_print_data:
    print(sequential_data)
    sys.exit(0)

print(f"Writing plots to directory: {plots_path}")

print("Creating sequential density plot ...")
# shows distribution of Artifact upload times
sequential_time_density = seaborn.kdeplot(data=sequential_data, x="total_time")
sequential_time_density.set(
    xlabel="Artifact Upload Time (Seconds)", title="Sequential Uploads Density of Artifact Upload Timigs"
)
sequential_time_density.figure.savefig(f"{plots_path}/sequential_time_density.png")
sequential_time_density.figure.clf()

print("Creating sequantial http status codes plot ...")
# shows count of different http status codes
sequential_http_status_code = seaborn.countplot(data=sequential_data, x="status_code")
sequential_http_status_code.set(
    xlabel="Artifact upload HTTP staus code", title="Sequential Artifacts Uploads HTTP Status Codes Received"
)

for i, bar in enumerate(sequential_http_status_code.patches):
    h = bar.get_height()
    sequential_http_status_code.text(
        i,
        h + 2000,
        f"{int(h)}",
        ha="center",
        va="center",
    )

sequential_http_status_code.figure.savefig(f"{plots_path}/sequential_http_status_code.png")
sequential_http_status_code.figure.clf()

print("Creating sequential artifact upload time over time plot ...")
# shows upload Artifact duration over time
sequential_artifact_upload_timings_over_time = seaborn.lineplot(data=sequential_data, x="artifact_num", y="total_time")
sequential_artifact_upload_timings_over_time.set(
    xlabel="Number Artifact uploaded",
    ylabel="Artifact upload time (Seconds)",
    title="Sequential Uploads Artifact Upload Timings During Benchmark",
)
sequential_artifact_upload_timings_over_time.figure.savefig(
    f"{plots_path}/sequential_artifact_upload_timings_over_time.png"
)
sequential_artifact_upload_timings_over_time.figure.clf()
