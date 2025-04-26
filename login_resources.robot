*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
Input Username
    [Arguments]    ${tên_người_dùng}
    Input Text    xpath://input[@name='username']    ${tên_người_dùng}

Input Password
    [Arguments]    ${mật_khẩu}
    Input Text    xpath://input[@name='password']    ${mật_khẩu}

Click Login Button
    Click Button    xpath://button[@type='submit']