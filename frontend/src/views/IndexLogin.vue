<template>
  <div class="common-layout">
    <el-container>
      <el-header></el-header>
      <el-container>

        <el-main width="40%">
          <el-image style="width: 100%; height: 80%; user-select: none; pointer-events: none; margin-top: -40px;"
                    :src="'/cover.png'"/>
        </el-main>

        <el-aside width="40%" class="aside-content">

          <div class="content">

            <div class="container">
              <h1>聪明教务管理系统</h1>

              <div class="circle-icons" style="margin-bottom: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 21 21" fill="none">
                  <circle cx="10.5" cy="10.5" r="10.5" fill="#F34B4B"/>
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 21 21" fill="none">
                  <circle cx="10.5" cy="10.5" r="10.5" fill="#FFC700"/>
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 21 21" fill="none">
                  <circle cx="10.5" cy="10.5" r="10.5" fill="#1097F9"/>
                </svg>
              </div>

              <div class="input-fields">
                <el-input v-model="userId" prefix-icon="el-icon-user" placeholder="用户名" style="margin-bottom: 20px;">
                  <template #prepend>
                    <span style="font-size: small;">userId</span>
                  </template>
                </el-input>

                <el-input v-model="password" prefix-icon="el-icon-lock" placeholder="密码" show-password
                          style="margin-bottom: 30px;">
                  <template #prepend>
                    <span style="font-size: small;">password</span>
                  </template>
                </el-input>

                <el-select v-model="selected_term" class="m-2" placeholder="请选择学期">
                  <el-option v-for="term in terms" :key="term.term_name"
                             :label="term.term_name"
                             :value="term.term_name"/>
                </el-select>
              </div>

              <div>
                <el-button type="primary" round @click="login">登录</el-button>
              </div>

            </div>
          </div>
        </el-aside>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import axios from "axios";
import md5 from "md5";
import {ElMessage} from 'element-plus'


export default {
  // define a component
  name: "IndexLogin",
  components: {},

  // data of the component
  data() {
    return {
      userId: "",
      password: "",
      userName: "default",
      host: "http://127.0.0.1:9000",
      selected_term: "",

      terms: [{
        term_id: "",
        term_name: ""
      }],
    };
  },


  // methods of the component
  methods: {
    async get_term() {
      const apiUrl = `${this.host}/api/getterm`;
      try {
        // 发送 GET 请求
        const response = await axios.get(apiUrl);

        // 处理返回码不为200的时候，提示登录失败
        if (response.status !== 200) {
          ElMessage.error("获取学期信息失败");
          return;
        }

        // 处理登录成功后的逻辑
        ElMessage.success("获取学期信息成功");
        this.terms = response.data.map(term => {
          return {
            term_id: term.term_id,
            term_name: term.term_name
          };
        });
      } catch (error) {
        console.error("登录失败：", error);
        ElMessage.error("登录失败");
      }

    },

    async login() {
      const id = this.userId;
      const password = this.password;

      // 使用 md5 对密码进行摘要处理
      const hashedPassword = md5(id + password);

      const apiUrl = `${this.host}/api/login`;
      const requestBody = {
        id,
        password: hashedPassword,
      };

      try {
        // 发送 POST 请求
        const response = await axios.post(apiUrl, requestBody);


        // 处理返回码不为200的时候，提示登录失败
        if (response.data.status !== "Success") {
          ElMessage.error("登录失败：" + response.data.data);
          return;
        }

        // 处理登录成功后的逻辑
        ElMessage.success("登录成功");
        console.log("登录成功", response.data.data.roleId);
        if (response.data.data.roleId === 1) {
          this.$router.push({
            name: 'students',
            query: {userId: id, userName: response.data.data.userName, term: this.selected_term}
          });
        } else {
          this.$router.push({
            name: 'teachers',
            query: {userId: id, userName: response.data.data.userName, term: this.selected_term}
          });
        }
      } catch (error) {
        console.error("登录失败：", error);
        ElMessage.error("登录失败");
      }
    }
  },

  mounted: function () {
    this.get_term();
  }

}
</script>

<style scoped>
html,
body {
  height: 100%;
  overflow: hidden;
}


.common-layout {
  height: 90vh; /* Adjust this value as needed */

  overflow: hidden;
}

.common-layout::-webkit-scrollbar {
  display: none;
}

::-webkit-scrollbar {
  width: 0 !important;
}

::-webkit-scrollbar {
  width: 0 !important;
  height: 0;
}

.aside-content {
  display: flex;
  flex-direction: column;
  margin-top: 4%;
}

.content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #fff;
  padding: 20px;
  border-radius: 10px;
}

.container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 20px;
}

.input-fields {
  display: flex;
  flex-direction: column;
  width: 80%;
}


.circle-icons {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: center;
  margin: 20px;
  margin-left: 15px;
  margin-bottom: 5px;
}
</style>
