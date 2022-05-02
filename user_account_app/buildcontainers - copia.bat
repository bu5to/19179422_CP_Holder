docker build . -t user_account_app
cd ..
cd pass_app 
docker build . -t pass_app
cd ..
cd booker_app
docker build . -t booker_app
cd ..
cd tracing_app  
docker build . -t tracing_app
