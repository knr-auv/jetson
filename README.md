# jetson-v2
To run this program it is necessary to compile and copy darknet (library files too) to "autonomy/darknet". To compile darknet on windows please install CUDA and ideally cuDNN. Then follow instructions for [vcpkg installation](https://github.com/AlexeyAB/darknet). It is also necessary to compile yolo_cpp_dll from visual studio project (it is provided with darknet). In order to do this you need to change CUDA version in yolo_cpp_dll.vcxproj
   
    -open in 'wordpad'
    -find CUDA 10 (at the begining and eof)
    -change it to your version (working fine with 11.0)
    -open .sln and compile
    -copy library files to 'autonomy/darknet'
Last step is to   [download weigths](https://wutwaw-my.sharepoint.com/:u:/g/personal/01150165_pw_edu_pl/EbOjCGle2JpBnpO_et4xA1YBfM6_nlObg1fTe_3WApiJsg?e=ZVil8q "LearnpyQt") and put them in autonomy folder.