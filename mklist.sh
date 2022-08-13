aws s3 ls s3://vitessedata/download/ | awk '/bin$/{print $4}' > list.txt
aws s3 cp list.txt s3://vitessedata/download/
