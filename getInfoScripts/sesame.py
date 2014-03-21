import requests
import os

sesame_url="http://127.0.0.1:8080/openrdf-sesame"

def import_content(repository_name,filecontent):
	upload_link =sesame_url+"/repositories/"+repository_name+"/statements"
	headers= {
	"content-type":"application/x-turtle"
	}
	# f=open(file_path,"r")
	res = requests.put(upload_link,data=filecontent,headers=headers)
	# f.close()
	print res.text

if __name__=="__main__":
	file_name = "fs.ttl"
	file_path=os.path.abspath(file_name)
	repository_name ="iwaf1"
	upload_file(repository_name,file_path)