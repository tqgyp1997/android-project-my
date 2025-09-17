@echo off
echo 🚀 闲鱼任务执行器 Android APP 构建脚本
echo ==========================================

echo.
echo 📋 检查环境...

:: 检查Java环境
java -version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Java未找到，请安装JDK 8或更高版本
    echo 💡 下载地址: https://adoptium.net/
    pause
    exit /b 1
)

echo ✅ Java环境检查通过

:: 检查是否有Android设备连接（可选）
adb devices > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  ADB未找到，将只构建APK文件，不自动安装
    set SKIP_INSTALL=1
) else (
    echo ✅ ADB环境检查通过
)

:: 检查设备连接（如果ADB可用）
if not defined SKIP_INSTALL (
    for /f "skip=1 tokens=1" %%i in ('adb devices') do (
        if not "%%i"=="" (
            set DEVICE_FOUND=1
            goto :device_check_done
        )
    )

    :device_check_done
    if not defined DEVICE_FOUND (
        echo ⚠️  未检测到Android设备，将只构建APK文件
        echo.
        echo 💡 如需自动安装，请：
        echo    1. 连接Android设备到电脑
        echo    2. 在设备上启用"开发者选项"
        echo    3. 启用"USB调试"
        echo    4. 允许此电脑进行调试
        echo.
        set SKIP_INSTALL=1
    ) else (
        echo ✅ 检测到Android设备
    )
)

echo.
echo 🔧 开始构建APK...

:: 检查gradlew是否存在
if not exist "gradlew.bat" (
    echo ❌ gradlew.bat未找到，请确保在Android项目根目录运行此脚本
    pause
    exit /b 1
)

:: 清理项目
echo 🧹 清理项目...
call gradlew.bat clean
if %errorlevel% neq 0 (
    echo ❌ 项目清理失败
    pause
    exit /b 1
)

:: 构建Debug APK
echo 📦 构建Debug APK...
call gradlew.bat assembleDebug
if %errorlevel% neq 0 (
    echo ❌ APK构建失败
    pause
    exit /b 1
)

echo ✅ APK构建成功

:: 安装APK（如果设备可用）
if not defined SKIP_INSTALL (
    echo.
    echo 📱 安装到设备...

    call gradlew.bat installDebug
    if %errorlevel% neq 0 (
        echo ❌ APK安装失败，但APK文件已构建成功
        echo 📁 APK位置: app\build\outputs\apk\debug\app-debug.apk
        set SKIP_INSTALL=1
    ) else (
        echo ✅ APK安装成功
    )
)

echo.
if defined SKIP_INSTALL (
    echo 🎉 APK构建完成！
    echo.
    echo 📁 APK文件位置：
    echo    app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 📋 手动安装步骤：
    echo    1. 将APK文件传输到Android设备
    echo    2. 在设备上启用"未知来源"安装
    echo    3. 点击APK文件进行安装
    echo    4. 授予必要权限
) else (
    echo 🎉 构建和安装完成！
)
echo.
echo 📋 下一步操作：
echo    1. 在设备上打开"闲鱼任务执行器"应用
echo    2. 授予必要的权限（网络、存储等）
echo    3. 配置服务器地址：http://您的电脑IP:1888
echo    4. 点击"连接"按钮连接到分布式任务系统
echo    5. 查看连接状态和运行日志
echo.
echo 🔗 相关链接：
echo    - 分布式系统: http://localhost:1888
echo    - 现有系统: http://localhost:1887/admin#
echo.

pause
