from paver.easy import *


options(
    cef_source=Bunch(
        darwin='https://chromiumembedded.googlecode.com/files/cef_binary_3.1364.1094_macosx.zip',
    )
)


@task
def auto():
    import sys
    import os
    project_path = os.path.abspath(os.path.dirname(__file__))
    options.update({
        'platform': sys.platform,
        'project_path': project_path,
    })

@task
@consume_args
def build(args, options):
    sh('mkdir -p Build')
    for arg in args:
        sh('cd src/%s;GOARCH=386 GOPATH=%s go build' % (arg, options.project_path))
        sh('install_name_tool -change cef-cef-swigcxx.so @executable_path/../Frameworks/cef-cef-swigcxx.so src/%s/%s' % (arg, arg))
        sh('rm -rf Build/%s.app' % arg)
        sh('cp -R cef/xcodebuild/Release/cefclient.app Build/')
        sh('cd Build;mv cefclient.app %s.app' % arg)
        sh('rm -f Build/%s.app/Contents/MacOS/cefclient' % arg)
        sh('cp src/%s/%s Build/%s.app/Contents/MacOS/' % ((arg,)*3))
        sh('cp pkg/darwin_386/swig/cef-cef-swigcxx.so Build/%s.app/Contents/Frameworks' % arg)
        sh('cd Build/%s.app/Contents/Frameworks;mv "cefclient Helper.app" "%s Helper.app"' % (arg, arg))
        sh('cd "Build/%s.app/Contents/Frameworks/%s Helper.app/Contents/MacOS";mv "cefclient Helper" "%s Helper"' % ((arg,)*3))
        sh('cd Build/%s.app/Contents;sed -i.bak "s/cefclient/%s/g" Info.plist;rm -f Info.plist.bak' % (arg, arg))
        sh('cd Build/%s.app/Contents/Resources;mv cefclient.icns %s.icns' % (arg, arg))

@task
def build_cef(options):
    sh('cd src/cef;GOARCH=386 GOPATH=%s go install' % options.project_path)
    sh('cd src/cef;swig -go -c++ -outdir swig cef.swigcxx')
    sh('cd src/cef;g++ -c -fpic cef_wrap.cxx -I. -arch i386')
    sh('cd src/cef;g++ -c -fpic objc_wrapper.mm -I. -arch i386')
    sh('cd src/cef;g++ -shared -undefined dynamic_lookup cef_wrap.o objc_wrapper.o ../../cef/xcodebuild/Release/libcef_dll_wrapper.a -L../../cef/Release/ -lcef -lstdc++ -o cef-cef-swigcxx.so -arch i386')
    sh('cp src/cef/cef-cef-swigcxx.so pkg/darwin_386/swig/')
    sh('install_name_tool -change @executable_path/libcef.dylib "@executable_path/../Frameworks/Chromium Embedded Framework.framework/Libraries/libcef.dylib" pkg/darwin_386/swig/cef-cef-swigcxx.so')

@task
def bootstrap(options):
    import os.path
    url = options.cef_source[options.platform]
    file_name = os.path.basename(url)
    sh('curl -sS %s > cef.zip' % url)
    sh('unzip cef.zip')
    sh('mv %s cef' % os.path.splitext(file_name)[0])
    sh('rm cef.zip')
    sh('ln -Fs %s src/cef/' % os.path.abspath('cef/include'))
    sh('cd cef;chmod +x tools/change_mach_o_flags_from_xcode.sh')
    sh('cd cef;chmod +x tools/change_mach_o_flags.py')
    sh('cd cef;chmod +x tools/strip_from_xcode')
    sh('cd cef;chmod +x tools/strip_save_dsym')
    sh('cd cef;chmod +x tools/make_more_helpers.sh')
    sh('cd cef;xcodebuild GCC_VERSION=com.apple.compilers.llvmgcc42 GCC_TREAT_WARNINGS_AS_ERRORS=NO -target cefclient -sdk macosx -configuration Release')
