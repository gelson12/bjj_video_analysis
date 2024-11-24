#!/bin/bash


if [ -d "app.log" ]; then
    echo "app.log is a directory. Removing it..."
    rm -r app.log
    echo "Creating an empty app.log file..."
    touch app.log
elif [ ! -f "app.log" ]; then
    echo "app.log does not exist. Creating it..."
    touch app.log
    chmod 664 app.log

else
    echo "app.log is already a file."
    echo "ensuring file has appropriate permission to be written by any application"
    chmod 664 app.log
fi