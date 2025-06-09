##for using in /etc/profile.d on k8s nodes
export http_proxy=http://192.168.110.1:3128/
export https_proxy=http://192.168.110.1:3128/
export no_proxy="localhost,127.0.0.0/8,::1,.corp.local,k8smaster-01a,k8smaster-01b,avicon-01a,avicon-01b,192.168.120.10,192.168.220.10,192.168.110.101,192.168.130.0/24"
export NO_PROXY=$no_proxy
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy