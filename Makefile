all: gen


gen:
	bash mklist.sh
	python gendownload.py 
	hugo

server: gen
	hugo -D server

push: 
	$(info !!!!!!!!!!!!!!!!!!!!!!!!!!!!! )
	$(info !! Make sure you have done 'make gen' so docs/ is fresh )
	$(info !!!!!!!!!!!!!!!!!!!!!!!!!!!!! )
	rsync -e 'ssh -p 21098' -avz docs/ vitepkco@server206.web-hosting.com:public_html
