*** Settings ***
Library    SeleniumLibrary
Test Setup    Mở Trình Duyệt Tới Trang Đăng Nhập
Test Teardown    Close Browser
Resource    login_resources.robot

*** Test Cases ***
Đăng Nhập Thành Công
    Input Username    Admin
    Input Password    admin123
    Click Login Button
    Wait Until Page Contains Element    xpath://h6[text()='Dashboard']
    Element Text Should Be    xpath://h6[text()='Dashboard']    Dashboard

Đăng Nhập Thất Bại Với Thông Tin Sai
    Input Username    InvalidUser
    Input Password    invalid123
    Click Login Button
    Wait Until Page Contains Element    xpath://p[text()='Invalid credentials']
    Element Text Should Be    xpath://p[text()='Invalid credentials']    Invalid credentials

*** Keywords ***
Mở Trình Duyệt Tới Trang Đăng Nhập
    Open Browser    https://opensource-demo.orangehrmlive.com/web/index.php/auth/login    chrome
    Maximize Browser Window
    Wait Until Page Contains Element    xpath://input[@name='username']