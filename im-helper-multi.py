import tkinter as tk, os, subprocess, sys, queue, threading, time
from tkinter import messagebox
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

default_path = os.environ['USERPROFILE'] + "\Desktop"

num_worker_threads = 4

class Cache:
    res_f = False

q = queue.Queue()
threads = []

def workerfunc(q, thread_no):
    while True:
        task = q.get()
        if task is None:
            print(f'Arbeiter #{thread_no} erfolgreich gestoppt.')
            break
        print(f"Arbeiter #{thread_no}: Wandle {task} in JPG um...")
        l_file = len(task)
        args = 'magick "'+file_path+'/'+task+'" "'+file_path +'/'+task[:l_file-5]+'.jpg"'
        process = subprocess.Popen(args, shell=True)
        exitCode = process.wait()
        if exitCode != 0:
            print(f"Fehler beim Umwandeln von {task}: {exitCode}: {process.stderr}")
        
        time.sleep(2)
        q.task_done()
        print(f'Arbeiter #{thread_no} hat das Bild "{task}" erfolgreich umgewandelt.')

print(f"Starte {num_worker_threads} Arbeiter...")
# turn-on num_worker_threads
for i in range(num_worker_threads):
    worker = threading.Thread(target=workerfunc, args=(q, i), daemon=True)
    worker.start()
    threads.append(worker)
print(f"{num_worker_threads} Arbeiter erfolgreich gestartet.")

file_path = filedialog.askdirectory(initialdir=default_path)
 
file_list = []

for file in os.listdir(file_path):
    if os.path.isfile(os.path.join(file_path, file)) and file.endswith(".HEIC"):
        file_list.append(file)

if file_list == []:
    messagebox.showerror("Fehler", "Es befinden sich keine .HEIC-Bilder in diesem Ordner. Bitte das Programm neu starten und den Ordner mit den .HEIC-Bildern auswählen.")
    sys.exit()

l_file_list = str(len(file_list))

res = messagebox.askyesnocancel("Umwandlung starten", "Es werden " + l_file_list + " HEIC Dateien umgewandelt. Sind Sie sich sicher? (Originalbilder bleiben erhalten)")

if res == True:
    Cache.res_f = messagebox.askyesno("Alte HEIC-Bilder löschen", "Sollen die alten HEIC-Bilder gelöscht werden?")
    for file in file_list:
        q.put(file)
elif res == False:
    messagebox.showwarning("Umwandlung nicht gestartet", "Es wurden keine Bilder umgewandelt. Bitte das Programm neu starten.")
    sys.exit()
elif res == None:
    messagebox.showwarning("Vorgang abgebrochen", "Es wurden keine Bilder umgewandelt. Bitte das Programm neu starten.")
    sys.exit()
else:
    messagebox.showerror("Exit", "Fehlerhafte Abfrage")
    sys.exit()

# block until all tasks are done
q.join()

print(f"Arbeit erledigt. {num_worker_threads} Arbeiter werden gestoppt...")

for j in range(num_worker_threads):
    q.put(None)

for t in threads:
    t.join()

print(f"{num_worker_threads} Arbeiter gestoppt.")

if Cache.res_f == True:
        for file in file_list:
            file_name = file_path + "/" + file
            print("Lösche Datei", file_name)
            os.remove(file_name)

messagebox.showinfo("Umwandlung erfolgreich beendet", "Es wurden " + l_file_list + " HEIC Bilder in JPG umgewandelt.")

