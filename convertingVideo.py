from tkinter import filedialog
import time
import skvideo.io

filename = filedialog.askopenfile(
            initialdir="/",
            title="Pilih Gambar",
            filetypes=(
                ("vidio", "*"),
            )
        )
image = filename.name
start_time = time.time()
amount = skvideo.io.vread(image)
for frame in amount:
        print(frame.shape)
end_time = time.time()
processing_time = end_time - start_time
print("Time to convert: ", processing_time)
