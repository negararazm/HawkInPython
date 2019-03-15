FROM python:3.7.1

COPY hello.py /
ADD templates templates/
	
#RUN pip install pprint
#RUN pip install uuid
RUN pip install datetime
#RUN pip install psutil
RUN pip install numpy
RUN pip install pandas
RUN pip install matplotlib
RUN pip install Flask
RUN pip install Redis
RUN pip install Requests
EXPOSE 80
EXPOSE 8083

CMD [ "python", "./hello.py"]


