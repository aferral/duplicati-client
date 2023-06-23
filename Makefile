

export VERSION=1.0.0
export REPONAME=backup_duplicati
export REMOTE_REGISTRY=172.24.178.0:5001

docker-build:
	docker build . -t $${REPONAME}:$${VERSION}	

docker-push:
	echo  $${REMOTE_REGISTRY}/$${REPONAME}:$${VERSION}
	docker tag $${REPONAME}:$${VERSION} $${REMOTE_REGISTRY}/$${REPONAME}:$${VERSION}
	docker push $${REMOTE_REGISTRY}/$${REPONAME}:$${VERSION}
	docker rmi $${REMOTE_REGISTRY}/$${REPONAME}:$${VERSION}

docker-run:
	docker run -e DUPLICATI_HOST -e DUPLICATI_PASS --network host --rm $${REPONAME}:$${VERSION}  archivos_utiles 3600 1
