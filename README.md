# WatchFS
Real-time Remotely Monitored File System.

---

WatchFS is a file system developed in FUSE (Filesystem in User Space). It records the activity happening on the File System
in real-time and sends it to a remote server via REST API. The server collects the data and displays the statistics to the user
via a dashboard.

---

### Disclaimer
This project was built in [HackBU](https://devpost.com/software/watchfs) 2018 ( Hackathon at Binghamton university ) , in a span of 24 hours. and had won the first place as a best security hack project.

### Detailed description
WatchFS File System is mounted at any given path (mount point) on the user's machine. It then starts intercepting all the
filesystem calls happening over this mount point. Information from these filesystem calls (creating, deleting, writing a file,
etc.) is updated to a remote server via REST API. The filesystem call is then transparently sent to the underlying filesystem.
The remote server stores the aggregated information in a database. It provides a dashboard to the user where they can see the
statistics, charts and notifications about their filesystem.

### Features
* Completely transparent to the end user.
* Real-time remotely monitored.
* Multi-threaded and fault-tolerant client, so the REST API calls don't slow down/block the file system calls.
* Request queueing - for fault tolerance when the remote server is down.
* Real-time issuing of alert when malicious activity or malicious file is detected.
* Coded in Python and Flask framework. ( Yay! ) also had to use html/js/css for front end ( :( )

### Basic Working
![Basic Working](Capture.JPG)

---

### Potential uses

Such a system can potentially be used to store sensitive stuff, such as classified documents. In such situations, it is essential that we monitor all the file system activity and notify the admin about any potetial security breaches or anomalous behavior in real-time.

---

### Screenshots
![Screenshot 1](Screenshot-1.png)
![Screenshot 2](Screenshot-2.png)

---

### Authors
- [Kartik Deshpande](https://www.linkedin.com/in/kartik-deshpande/)
- [Vipul Chaskar](https://www.linkedin.com/in/vipul-chaskar-50808757/)
- [Sujoy Das](https://www.linkedin.com/in/sujoydas27/)
- [Nikhil Raverkar](https://www.linkedin.com/in/raverkar-nikhil/)
