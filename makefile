default:

update_apiclient:
	pip install --upgrade --force-reinstall git+https://github.com/sakalosj/qg_openapi_client.git

dc_up:
	cd docker &&\
	docker-compose -p qs up --build

dc_down:
	cd docker &&\
	docker-compose -p qs down

dc_clean:
	cd docker &&\
	docker-compose -p qs down -v
