import seaborn
import pandas

plots_path = "../plots"
csv_file = "../output/a01e5c74-sequential_upload-10.csv"
#  csv_file = "../output/0ebbd90c-sequential_upload-200.csv"

sequential_data = pandas.read_csv(csv_file)

print(sequential_data)

# shows distribution of function upload times
plot1 = seaborn.kdeplot(data=sequential_data, x="total_time")
plot1.set(xlabel="Function upload time")
plot1.figure.savefig(f"{plots_path}/plot1.png")
plot1.figure.clf()

# shows count of different http status codes
plot2 = seaborn.histplot(data=sequential_data, x="status_code")
plot2.set(xlabel="Function upload HTTP staus code")
plot2.figure.savefig(f"{plots_path}/plot2.png")
plot2.figure.clf()

# shows upload function duration over time
plot3 = seaborn.lineplot(data=sequential_data, x="artifact_num", y="total_time")
plot3.set(xlabel="Number function uploaded", ylabel="Function upload time")
plot3.figure.savefig(f"{plots_path}/plot3.png")
plot3.figure.clf()
