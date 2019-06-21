#!/usr/bin/env python

import os,sys
import time
import getpass
import re
import subprocess
import ConfigParser
try:
	from Tkinter import *
	import tkMessageBox
	import tkFileDialog
except:
	print("Please install Tkinter on your system")
	sys.exit()

currentDir = os.getcwd()
master = Tk()
master.resizable(width=FALSE, height=FALSE)
master.wm_title("Kafka Management Tool")

exists = os.path.isfile(currentDir + "/Kafka.conf")
if exists:
	print("Config file exists")
	configFile = "Kafka.conf"
	cfg = ConfigParser.ConfigParser()
	cfg.read(configFile)

	directory = cfg.get("Kafka","directory")
	config = cfg.get("Kafka","config")
	kafkaZk = cfg.get("Config","kafka-zookeeper")
	kafkaBrokers = cfg.get("Config","kafka-brokers")
	replication = cfg.get("Config","topic-replication-factor")
	partitions = cfg.get("Config","topic-partitions")
else:
	print("Config file does not exist. Using local defaults.")
	directory = "/opt/kafka_2.12-1.1.0/bin/"
	config = "/opt/kafka_2.12-1.1.0/config/"
	kafkaZk = "localhost:2181"
	kafkaBrokers = "localhost:9092"
	replication = "1"
	partitions = "1"

kafkaOn = 0

def startKafka():
	startCmd = directory + "kafka-server-start.sh"
	startArgs = config + "server.properties"
	subprocess.Popen(["sudo", startCmd, startArgs])
	startButton.configure(bg="chartreuse", activebackground="pale green")
	textBox.delete(1.0,END)
	textBox.insert(END, getTopics())
	kafkaOn=1

def stopKafka():
	stopCmd = directory + "kafka-server-stop.sh"
	clearLock()
	subprocess.Popen(["sudo", stopCmd])
	startButton.configure(bg="orange red", activebackground="tomato")
	kafkaOn=0

def clearLock():
	subprocess.Popen(["sudo", "rm", "-rf", "subprocess.Popen"])

def getTopics():
	return os.popen(directory + "kafka-topics.sh --zookeeper " + kafkaZk + " --list").read()

def refreshTopics():
	textBox.delete(1.0,END)
	textBox.insert(END, getTopics())

def createTopic():
	if len(e.get()) > 0:
		subprocess.Popen([directory+"kafka-topics.sh","--create","--zookeeper", kafkaZk,"--replication-factor", replication, "--partitions", partitions, "--topic", e.get()])
		time.sleep(10)
		textBox.delete(1.0,END)
		textBox.insert(END, getTopics())
	else:
		tkMessageBox.showwarning("Warning", "Please specify a topic name")

def deleteTopic():
	if len(e.get()) > 0:
		subprocess.Popen([directory+"kafka-topics.sh","--delete","--zookeeper", kafkaZk, "--topic", e.get()])
		time.sleep(10)
		textBox.delete(1.0,END)
		textBox.insert(END, getTopics())
	else:
		tkMessageBox.showwarning("Warning", "Please specify a topic name")

def recreateTopic():
	if len(e.get()) > 0:
		subprocess.Popen([directory+"kafka-topics.sh","--delete","--zookeeper", kafkaZk, "--topic", e.get()])
		time.sleep(10)
		subprocess.Popen([directory+"kafka-topics.sh","--create","--zookeeper", kafkaZk,"--replication-factor", replication, "--partitions", partitions, "--topic", e.get()])
		time.sleep(10)
		textBox.delete(1.0,END)
		textBox.insert(END, getTopics())
	else:
		tkMessageBox.showwarning("Warning", "Please specify a topic name")

def purgeTopic():
	if len(e.get()) > 0:
		subprocess.Popen([directory+"kafka-configs.sh","--zookeeper", kafkaZk, "--entity-type", "topics", "--alter", "--entity-name", e.get(), "--add-config", "retention.ms=1"])
		time.sleep(10)
		subprocess.Popen([directory+"kafka-configs.sh","--zookeeper", kafkaZk, "--entity-type", "topics", "--alter", "--entity-name", e.get(), "--add-config", "retention.ms=86400000"])
		textBox.delete(1.0,END)
		textBox.insert(END, getTopics())
	else:
		tkMessageBox.showwarning("Warning", "Please specify a topic name")

def submitMessage():
	prodWin = Toplevel()
	prodWin.title("Submit Message")
	Label(prodWin, text="Topic").grid(row=0)
	Label(prodWin, text="Message").grid(row=1)
	e1 = Entry(prodWin)
	e2 = Entry(prodWin)
	e1.grid(row=0, column=1, columnspan=2, padx=5, pady=10)
	e2.grid(row=1, column=1, columnspan=2, padx=5, pady=10)
	prodButton = Button(prodWin, text="Submit", width=10, command=lambda: submit(prodWin, e1.get(), e2.get()), bg="dark grey")
	prodButton.grid(row=2, column=0, padx=5, pady=5)
	clearButton = Button(prodWin, text="Clear", width=10, command=lambda: (e1.delete(0, END), e2.delete(0, END)), bg="dark grey")
	clearButton.grid(row=2, column=1, padx=2, pady=5)
	cancelButton = Button(prodWin, text="Cancel", width=10, command=lambda: (prodWin.destroy()), bg="dark grey")
	cancelButton.grid(row=2, column=2, padx=5, pady=5)
	prodWin.mainloop()

def submit(prodin, topic, msg):
	os.system("echo \"" + msg + "\" | " + directory+"kafka-console-producer.sh --broker-list " + kafkaBrokers + " --topic " + topic)

def exist():
	clearLock()
	master.destroy()

def runningBg():
	runningVal = os.popen("sudo ps -ef | grep kafka | wc -l").read()
	if int(runningVal) > 2:
		kafkaOn = 1
		return "chartreuse"
	else:
		kafkaOn = 0 
		return "orange red"

def runningAb():
	runningVal = os.popen("sudo ps -ef | grep kafka | wc -l").read()
	if int(runningVal) > 2:
		kafkaOn = 1
		return "pale green"
	else:
		kafkaOn = 0 
		return "tomato"

top = Frame(master)
top.grid(row=0, column=0)
bottom = Frame(master, bd=10)
bottom.grid(row=1, column=0)
right = Frame(master)
right.grid(row=0, column=1, rowspan=2)

buttonFrame = Frame(top, bd=5)
buttonFrame.pack()

e = Entry(master, text="Topic Name", width=40)
L1 = Label(master, text="Topic Name: ")
clearButton = Button(master, text="x", command=lambda: e.delete(0, END), bg="dark gray", height=1)
L1.pack(in_=top, side=LEFT)
e.pack(in_=top, side=LEFT)
clearButton.pack(in_=top, side=RIGHT)
e.focus_set()
startButton = Button(master, text="Start Kafka", width=30, command=startKafka, bg=runningBg(), activebackground=runningAb())
startButton.pack(in_=bottom)
stopButton = Button(master, text="Stop Kafka", width=30, command=stopKafka)
stopButton.pack(in_=bottom)
createTopicButton = Button(master, text="Create Kafka Topic", width=30, command=createTopic)
createTopicButton.pack(in_=bottom)
deleteTopicButton = Button(master, text="Delete Kafka Topic", width=30, command=deleteTopic)
deleteTopicButton.pack(in_=bottom)
recreateTopicButton = Button(master, text="Recreate Kafka Topic", width=30, command=recreateTopic)
recreateTopicButton.pack(in_=bottom)
purgeTopicButton = Button(master, text="Purge Kafka Topic", width=30, command=purgeTopic)
purgeTopicButton.pack(in_=bottom)
refreshTopicButton = Button(master, text="Refresh Kafka Topic List", width=30, command=refreshTopics)
refreshTopicButton.pack(in_=bottom)
submitMessageButton = Button(master, text="Submit Kafka Mesage", width=30, command=submitMessage)
submitMessageButton.pack(in_=bottom)
quitButton = Button(master, text="Exit", width=30, command=exist)
quitButton.pack(in_=bottom)

scroll = Scrollbar(master)
textBox = Text(master, height=20, width=45)
scroll.pack(in_=right,side=RIGHT, fill=Y)
textBox.pack(in_=right,side=LEFT, fill=Y)
scroll.config(command=textBox.yview)
textBox.config(yscrollcommand=scroll.set)
textBox.insert(END, getTopics())

mainloop()
