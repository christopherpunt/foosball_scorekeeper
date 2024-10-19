# Introduction 
This project is an automated scorekeeper for the game of foosball, implemented using Python with Flask as the API between the microcontrollers and the backend service. The primary objective is to provide a convenient and efficient way to track scores during foosball matches, eliminating the need for manual scorekeeping.

# Getting Started
1.	Installation process
    * Install python to your machine (version built with 3.12.1)
2.	Software dependencies
    * install dependencies for this project\
        pip install -r requirements.txt
3.	Latest releases
4.	API references

# Build and Test
TODO: Describe and show how to build your code and run the tests. 

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

# Screenshots and video demo

https://github.com/christopherpunt/foosball_scorekeeper/assets/43280249/74b661bc-6de4-4149-ba19-00ef0c06a4fa

<img width="1727" alt="Screenshot 2024-02-23 at 8 23 54 PM" src="https://github.com/christopherpunt/foosball_scorekeeper/assets/43280249/03553280-d2ee-4007-8685-ff9176768d25">

<img width="1728" alt="Screenshot 2024-02-23 at 8 24 21 PM" src="https://github.com/christopherpunt/foosball_scorekeeper/assets/43280249/5c6459dc-2bda-453f-ae27-0f88ea3953cd">

<img width="1728" alt="Screenshot 2024-02-23 at 8 24 33 PM" src="https://github.com/christopherpunt/foosball_scorekeeper/assets/43280249/d7e45d90-d972-45e4-9ec2-adbbe6ea99cc">

<img width="1728" alt="Screenshot 2024-02-23 at 8 25 07 PM" src="https://github.com/christopherpunt/foosball_scorekeeper/assets/43280249/41fccb8e-0225-45c5-a150-751802ce08e5">

<img width="1728" alt="Screenshot 2024-02-23 at 8 25 24 PM" src="https://github.com/christopherpunt/foosball_scorekeeper/assets/43280249/e396ab92-3735-4b01-95cb-663be707d6f5">


Containerization
# how to build
podman build -t foosball .

# how to run
podman run -d -p 5001:5001 -v ./db_instance:/instance foosball