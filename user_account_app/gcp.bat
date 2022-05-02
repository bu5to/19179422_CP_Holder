docker build . -t gcr.io/soft7011-jorge/user_account_app:version1.0
cd ..
cd pass_app 
docker build . -t gcr.io/soft7011-jorge/pass_app:version1.0
cd ..
cd booker_app
docker build . -t gcr.io/soft7011-jorge/booker_app:version1.0
cd ..
cd tracing_app  
docker build . -t gcr.io/soft7011-jorge/tracing_app:version1.0
