# Qchat
## Description
### ChatRoom Part
user can register Qchat system and browse 


## API REFERENCE

### 总体标准

权限验证模块暂时没有，以后可能添加，注意一下预留

所有API使用json格式，返回值都将包括error_code和error_msg，其中，error_code为0代表成功，不为0则为具体的错误代码，详细查询api-error-code.md文件。

以下文档中没有特别标注的，都采用GET方式，使用其他方式的会特别注明

### user部分

- /user/login

**功能:** 登录，获取usertoken  
**参数:** user_phone, user_password（已使用sha1加密过的）  
**返回值:** 
```
{"user_token":"IzmegwM4VFEstje8tKHkuu5vaNkAy7M6xZbDmOx7j2pDctBv49FouBKueUVCSxzf","expires_in":1454485964,"error_code":0,"error_msg":""}
```
**可能的错误:**
```
{"error_code":2,"error_msg":"Invalid username or password."}
```

- /user/register

**功能:** 注册 
**参数:** user_phone, user_password（已使用sha1加密过的） 
**返回值:** 
```
{"user_token":"IzmegwM4VFEstje8tKHkuu5vaNkAy7M6xZbDmOx7j2pDctBv49FouBKueUVCSxzf","expires_in":1454485964,"error_code":0,"error_msg":""}
``` 
**可能的错误:**
```
{"error_code":3,"error_msg":"Register failed!"}
{"error_code":4,"error_msg":"Username already exists!"}
{"error_code":5,"error_msg":"Invalid input."}
```

- /user/change_password

**功能:** 修改管理员密码
**参数:** user_phone, user_password, new_password（已使用sha1加密过的）  
**可能的错误:**
```
{"error_code":2,"error_msg":"Invalid username or password."}
{"error_code":5,"error_msg":"Invalid input."}
```

- /user/change_waimai_password

**功能:** 修改平台密码  
**参数:** user_token, new_password, type 1为百度 2为美团 3为饿了吗 , user_name 账户名
**可能的错误:**
```
{"error_code":7,"error_msg":"Failed to change waimai password."}
```

- /user/uploadlogo

**功能:** 上传或更新logo  
**参数:** user_token
**可能的错误:**
```
{"error_code":23,"error_msg":"Failed to upload logo."}
```

- /order/getHistoryList

**功能:** 获得历史订单 
**参数:** order_platform order_type order_status order_bdate order_edate offset（页数 从0开始） limit
**返回值:** 
```
外卖单列表
total 为总数
result 为订单列表 
其中的items 为该行对应的items
``` 
**可能的错误:**
```
{"error_code":6,"error_msg":"No results!"}
```

- /user/get_waimai_password

**功能:** 获得平台密码
**参数:** user_token
**返回值:** 三个平台的密码和用户名 字段mt bd el为密码 添加后缀name为相应用户名
**可能的错误:**
```
{"error_code":9,"error_msg":"Failed to get waimai password."}
```

- /user/check_waimai_password

**功能:** 检查已设置的平台密码是否正确
**参数:** user_token, type 1为百度 2为美团 3为饿了吗
**返回值:** status 0为错误 1为正确
**可能的错误:**
```
{"error_code":9,"error_msg":"Failed to get waimai password."}
```

- /user/get_user_info

**功能:** 获得用户信息
**参数:** user_token
**返回值:** 对应user信息
**可能的错误:**
```
{"error_code":13,"error_msg":"Failed to get user info."}
```

- /user/get_print_config

**功能:** 获得打印参数 如果用户未设置过 直接设置为默认值
**参数:** user_token
**返回值:** 对应user的打印参数
**可能的错误:**
```
{"error_code":11,"error_msg":"Failed to get print_config."}
```

- /user/sendPhoneCode

**功能:** 获取短信验证码
**参数:** user_phone  
**返回值:** 无
**可能的错误:**
```
20, "Making too many request in a short period of time."  
21, "Invalid phone number."  
```

- /user/loginByCode

**功能:** 通过短信验证码登陆（如果未注册，将会自动创建账号）  
**参数:** user_phone, user_code  
**返回值:** user_token  
**可能的错误:**
```
21, "Invalid phone number."  
22, "Invalid phone code."
```


- /user/save_print_config

**功能:** 修改或保存打印参数 
**参数:** 
user_token 
auto_print
items_per_page
intervaltime
mode
preset
content
printer
papertype
brand
**返回值:** echoResult
**可能的错误:**
```
{"error_code":12,"error_msg":"Failed to save print_config."}
```

- /order/getRevenueRate

**功能:** 获取不同平台交易额比例
**参数:** period（1天 7天 180天 传数字就行）  
**返回值:** 
```
{"costrate":{"b":0,"m":66.0294806187,"e":33.9705193813},"cost":{"b":0,"m":156680.1,"e":80608},"totalcost":237288.1,"ordernum":{"b":0,"m":8323,"e":1896},"totalordernum":10219,"error_code":0,"error_msg":""}
costrate为三大平台营业额百分比
cost为三大平台营业额
total为求和
orderum为三大平台订单数
averagecost为平均花费
``` 
**可能的错误:**
```
{"error_code":8,"error_msg":"Failed to get revenue rate."}

- /order/getOrderItemRank

**功能:** 获取orderitem排名 按交易额 或者 按交易量
**参数:** period（1天 7天 180天 传数字就行) type 0 for quantity 1 for price 
**返回值:** 
```
按顺序排列 每列为 title pricesum quantitysum
``` 
**可能的错误:**
```
{"error_code":10,"error_msg":"Failed to get order_item rank."}

### 远程平台部分
网站打开后，分为以下4个步骤  
1. getCaptcha获取验证码，让用户输入后提交
2. login获取外卖平台的登陆凭证
3. 使用第二部获取的登陆凭证，通过fetchRemoteOrder同步订单，同时读取进度
4. 上一步中进度满了以后，开始隔30s发起一次fetchNewOrder

- /remote/getCaptcha  
**功能:** 获取百度登陆用的验证码  
**参数:** user_token  
**返回值:**  
```
captcha_token: 验证码代号  
captcha_image: 验证码图片地址  
bd_password: 用户的百度密码（用法见下一步API）  
```

- /remote/login  
**功能:** 服务器发起外卖平台的登陆请求并返回凭证  
**参数:** user_token, captcha_token，captcha_code(用户输入的验证码), bd_encrypt_password(加密后的百度密码)  
**返回值:** 成功后返回mt,el,bd字段，需要保存在本地，之后发起订单同步、抓取新订单等需要使用的外卖网站登录后的usertoken一类的东西  
失败后返回值：  
```
15, "Invalid meituan username or password"  
16, "Invalid eleme username or password"  
17, "Invalid baidu username or password"  
18, "Invalid captcha"  
```
bd_encrypt_password的目的为，百度在登陆时不是使用明文登陆，而是用自己写的可逆加密算法，这个用js调用它的库比较方便，服务器不方便执行js所以放到前端执行，获取方式为：（其中baidu_original_password替换成上一步中获取的bd_password）  
```
<script src="https://wmpass.baidu.com/static/passport/pkg/common_0587d74.js"></script>
<script>
	SimpleEncrypt=require("passport:static/utils/Base64Encrypt.js");
	console.log(SimpleEncrypt.simplencrypt("baidu_original_password"));
</script>
```

- /order/fetchRemoteOrder

**功能:** 发起订单同步（从外卖服务器抓取订单）当用户打开网站后，即发起  
**参数:** user_token, bd, mt, el(POST方式，login那个接口获取的，直接以字符串传入即可)  
**返回值:** 无  

- /order/getFetchStatus

**功能:** 查看订单同步状态  
**参数:** user_token  
**返回值:** 返回的json包含status字段，processing为处理中, idle为空闲  

- /order/fetchNewOrder

**功能:** 查看是否有新订单  
**参数:** user_token, timestamp, bd, mt, el(POST方式，login那个接口获取的，直接以字符串传入即可)  
**返回值:** 返回的json包含count字段和orders  
