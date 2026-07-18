"""
GUI for Network Device Monitor
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import datetime
import threading

from scanner import scan_network, get_local_network
from monitor import NetworkMonitor


class NetworkMonitorGUI:

    REFRESH_TIME = 5000

    def __init__(self):

        # --------------------------
        # Monitor Object
        # --------------------------
        self.monitor = NetworkMonitor()

        self.scanning = False

        # --------------------------
        # Main Window
        # --------------------------
        self.root = tk.Tk()

        self.root.title("Network Device Monitor")

        self.root.geometry("1100x650")

        self.root.minsize(900, 500)

        # --------------------------
        # Title
        # --------------------------
        title = tk.Label(
            self.root,
            text="Network Device Monitor",
            font=("Arial", 22, "bold")
        )

        title.pack(pady=10)
        self.network_label = tk.Label(
            self.root,
            text=f"Network : Local Network",
            font=("Arial", 11)
        )

        self.network_label.pack()

        # --------------------------
        # Top Frame
        # --------------------------
        top_frame = tk.Frame(self.root)

        top_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Label(
            top_frame,
            text="Search :",
            font=("Arial", 12)
        ).pack(side="left")

        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            top_frame,
            textvariable=self.search_var,
            width=30,
            font=("Arial", 12)
        )

        self.search_entry.pack(
            side="left",
            padx=10
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.update_table()
        )

        self.scan_button = tk.Button(
            top_frame,
            text="Scan Network",
            font=("Arial", 12, "bold"),
            command=self.start_scan
        )



        self.scan_button.pack(
            side="right"
        )

        self.export_button = tk.Button(
        top_frame,
        text="Export CSV",
        command=self.export_csv
        )

        self.export_button.pack(side="right", padx=5)

        # --------------------------
        # Treeview Frame
        # --------------------------
        tree_frame = tk.Frame(self.root)

        tree_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "IP Address",
            "MAC Address",
            "Vendor",
            "Hostname",
            "Status",
            "First Seen",
            "Last Seen"
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings"
        )

        for col in columns:

            self.tree.heading(
                col,
                text=col
            )

            self.tree.column(
                col,
                width=150,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.pack(
            fill="both",
            expand=True
        )

        # --------------------------
        # Status Colors
        # --------------------------
        self.tree.tag_configure(
            "Online",
            foreground="green"
        )

        self.tree.tag_configure(
            "Offline",
            foreground="red"
        )

        self.tree.tag_configure(
            "New",
            foreground="blue"
        )

        # --------------------------
        # Bottom Frame
        # --------------------------
        bottom = tk.Frame(self.root)
        footer = tk.Label(
            self.root,
            text="Developed by Himanshu Rawat\nPython • Scapy • Tkinter",
            font=("Arial", 9),
            fg="lightgray",
            bg="#2b2b2b"
        )       

        footer.pack(side="bottom", pady=5)
        bottom.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.total_label = tk.Label(
            bottom,
            text="Total Devices : 0",
            font=("Arial", 12, "bold")
        )

        self.total_label.pack(
            side="left",
            padx=10
        )

        self.online_label = tk.Label(
            bottom,
            text="Online : 0",
            font=("Arial", 12, "bold")
        )

        self.online_label.pack(
            side="left",
            padx=10
        )

        self.offline_label = tk.Label(
            bottom,
            text="Offline : 0",
            font=("Arial", 12, "bold")
        )

        self.offline_label.pack(
            side="left",
            padx=10
        )

        self.status_label = tk.Label(
            bottom,
            text="Last Scan : Never",
            font=("Arial", 11)
        )

        self.status_label.pack(
            side="right"
        )
    # -----------------------------------------
    # Start Scan
    # -----------------------------------------
    def start_scan(self):

        if self.scanning:
            return
        self.network_label.config(
            text=f"Network : Local Network"
        )

        self.scanning = True

        self.scan_button.config(
            text="Scanning...",
            state="disabled"
        )

        thread = threading.Thread(
            target=self.scan_worker,
            daemon=True
        )

        thread.start()

    # -----------------------------------------
    # Background Scan
    # -----------------------------------------
    def scan_worker(self):

        try:

            devices = scan_network(get_local_network())

            self.monitor.update(devices)

            self.root.after(
                0,
                self.update_table
            )

        except Exception as e:

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Scan Error",
                    str(e)
                )
            )

        finally:

            self.root.after(
                0,
                self.scan_finished
            )

    # -----------------------------------------
    # Scan Finished
    # -----------------------------------------
    def scan_finished(self):

        self.scanning = False

        self.scan_button.config(
            text="Scan Network",
            state="normal"
        )

        self.root.after(
            self.REFRESH_TIME,
            self.start_scan
        )

    # -----------------------------------------
    # Update Table
    # -----------------------------------------
    def update_table(self):

        search = self.search_var.get().lower()

        for row in self.tree.get_children():

            self.tree.delete(row)

        devices = self.monitor.get_devices()

        online = 0
        offline = 0

        for device in devices:

            values = (
                device["ip"],
                device["mac"],
                device["vendor"],
                device["hostname"],
                device["status"],
                device["first_seen"],
                device["last_seen"]
            )

            text = " ".join(
                str(x).lower()
                for x in values
            )

            if search:

                if search not in text:
                    continue

            self.tree.insert(
                "",
                tk.END,
                values=values,
                tags=(device["status"],)
            )

            if device["status"] == "Online":
                online += 1

            elif device["status"] == "Offline":
                offline += 1

        self.total_label.config(
            text=f"Total Devices : {len(devices)}"
        )

        self.online_label.config(
            text=f"Online : {online}"
        )

        self.offline_label.config(
            text=f"Offline : {offline}"
        )

        self.status_label.config(
            text="Last Scan : " +
            datetime.now().strftime("%H:%M:%S")
        )

    # -----------------------------------------
    # Run GUI
    # -----------------------------------------

    def export_csv(self):

        devices = self.monitor.get_devices()

        if not devices:
            messagebox.showwarning(
                "No Data",
                "There are no devices to export."
            )
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="network_devices.csv"
        )

        if not filename:
            return

        try:

            with open(filename, "w", newline="") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "IP Address",
                    "MAC Address",
                    "Vendor",
                    "Hostname",
                    "Status",
                    "First Seen",
                    "Last Seen"
                ])

                for device in devices:

                    writer.writerow([
                        device["ip"],
                        device["mac"],
                        device["vendor"],
                        device["hostname"],
                        device["status"],
                        device["first_seen"],
                        device["last_seen"]
                    ])

            messagebox.showinfo(
                "Success",
                "Devices exported successfully!"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )
    def run(self):

        self.root.after(
            1000,
            self.start_scan
        )

        self.root.mainloop()


# -----------------------------------------
# Run directly
# -----------------------------------------
if __name__ == "__main__":

    app = NetworkMonitorGUI()

    app.run()        
