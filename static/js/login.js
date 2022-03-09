(function ($, window) {
  "use strict";

  const $bt1 = $("#bt1");
  const $bt2 = $("#bt2");

  window.onload = function () {
    if ($bt1 && $bt1.length) {
      $bt1[0].addEventListener("click", sign_in);
    }
    if ($bt2 && $bt2.length) {
      $bt2[0].addEventListener("click", signup);
    }
  };
  function signup(event){
    event.preventDefault();
    window.location.href='/signup'
  }

  function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
  }

  function is_email(asValue) {
    var regExp = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;
    return regExp.test(asValue);
  }

  function sign_in(event) {
    event.preventDefault();
    let $useremail = $("#input-email");
    let $password = $("#password");
    // 이런건 방어 코드
    // 혹시나 무슨 일때문에 찾을 수 없으면 $useremail 변수는 undefined 인데
    // undefined 에서 val 같은 메서드 쓰려고 하면 에러남
    // 에러는 항상 안나게 방어 처리 해주는게 필수
    if (!$useremail || !$password) {
      return;
    }
    const useremail = $useremail.val();
    const password = $password.val();
    if (!useremail) {
      alert("이메일을 입력해주세요.");
      $useremail.focus();
      return;
      // 이런식으로 분기하면 됨
    } else if (!is_email(useremail)) {
      alert("이메일 형식이 아닙니다.");
      $useremail.focus();
      return;
    }

    if (!password) {
      alert('비밀번호를 입력해주세요.')
      $password.focus();
      return;
    } else if (!is_password(password)) {
      alert('비밀번호 규칙에 맞지 않습니다.')
      $password.focus();
      return;
    }

    $.ajax({
      type: "POST",
      url: "/sign_in",
      data: {
        useremail_give: useremail,
        password_give: password,
      },
      success: function (response) {
        console.warn('response["result"] : ', response["result"]);
        if (response["result"] == "success") {
          $.cookie("mytoken", response["token"], {path: "/"});
          window.location.replace("/index");
        } else {
          alert(response["msg"]);
        }
      },
    });
  }

})(jQuery, window);
