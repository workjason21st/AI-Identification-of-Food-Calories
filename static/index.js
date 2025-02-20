let cameraStream = null;
const baseURL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://127.0.0.1:5000';

document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("click", (event) => {
    const action = event.target.dataset.action;
    if (!action) return;
  
    switch (action) {
      case "showHistory":
        stopCamera();
        showHistory(1);
        break;
      case "chooseFromAlbum":
        $(".detectFoodContainer").show();
        $(".historyContainer").hide();
        $('.HomeContainer').hide();
        $('#imagebox').hide();
        $("#imageinput").click();
        break; 
      case "takePhoto":
        startCamera();
        break;
      case "takePhotoAgain":
        $("#takePhoto").click();
        break;
      case "captureButton":
        capturePhoto();
        break;
      case "processImage":
        processImage();
        break;
    }
  });
  window.addEventListener("load", () => {
    // 當選擇圖片時，顯示預覽與按鈕並停止相機
    $('#imageinput').change(function() {
        stopCamera();
        readUrl(this);
        $('#imagebox').fadeIn(500);
        $('#processImage').fadeIn(500);
        $('#captureButton, #takePhotoAgain').fadeOut(500);
    });
  });
});

/*
  $('#calendarbutton').click(() => {
      const calories = $("#testresults").text();
      if (calories) {
          $.ajax({
              url: `${baseURL}/addToCalendar`,
              type: "POST",
              data: JSON.stringify({ calories: calories }),
              contentType: "application/json",
              success: function(response) {
                  alert("卡路里已記錄到 Google 日曆中");
              }
          });
      } else {
          alert("請先辨識食物熱量");
      }
  });*/

// **開啟相機**
function startCamera() {
  $('.HomeContainer').hide();
  $('.detectFoodContainer').fadeIn(500);
  $('.historyContainer').fadeOut(500);
  const video = document.getElementById("cameraStream");
  // 使用 getUserMedia 來訪問相機
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      cameraStream = stream;
      video.srcObject = stream;
      video.play();
      $('#cameraContainer').show();
      $('#captureButton').show();
      
      $('#processImage, #takePhotoAgain, #imagebox').hide();
      $('#testresults').html('');
    })
    .catch(error => {
      console.error("相機訪問失敗:", error);
      alert("無法訪問相機");
    }
  );
}

function capturePhoto() {
  const video = document.getElementById("cameraStream");
  const canvas = document.getElementById('photoCanvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  // 停止相機
  stopCamera();
  // 顯示拍攝的照片
  const imageDataUrl = canvas.toDataURL('image/jpeg');
  $('#imagebox').show();
  $('#imagebox').attr('src', imageDataUrl);
  // 將拍攝的照片設置為 imageinput 的值
  const file = dataURLtoFile(imageDataUrl, 'captured-photo.jpg');
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  $('#imageinput')[0].files = dataTransfer.files;
  // 顯示重新拍照和辨識熱量的按鈕
  $('#processImage, #takePhotoAgain').show();
}

// 處理照片
function processImage() {
  let imagebox = $('#imagebox');
  let input = $('#imageinput')[0]
  if(input.files && input.files[0]) {
    let formData = new FormData();
    formData.append('image', input.files[0]);

    $('#testresults').html('');
    $('#loading').show(); // 顯示讀條
    $.ajax({
      url: `${baseURL}/detectObject`,
      type: "POST",
      data: formData,
      cache: false,
      processData: false,
      contentType: false,
      error: function(xhr, status, error) {
        console.error("上傳錯誤:", error);
        console.log("伺服器回應:", xhr.responseText);
        $('#loading').hide(); // 隱藏讀條
        alert("辨識失敗，請稍後再試！");
      },
      success: function(data) {
        console.log(data);
        var result = data['results'];
        $("#testresults").html(result)

        bytestring = data['status']
        image = bytestring.split('\'')[1]
        let imageUrl = 'data:image/jpeg;base64,' + image;
        imagebox.attr('src', imageUrl);

        //let image_path = data['image_path'];
        //imagebox.attr('src', imageUrl);
        $('#loading').hide(); // 隱藏讀條
        // 存入歷史紀錄
        if (data.labels != 0) {
          saveHistory(imageUrl, data.labels, data.calories);
        }
      }
    });
  }else {
    alert("請先上傳食物照片");
  }
}  

// **停止相機**
function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop()); // 停止所有相機串流
    cameraStream = null; // 清除變數
  }
  $('#cameraContainer, #captureButton').hide(); // 隱藏相機畫面
}

function readUrl(input) {
  imagebox = $('#imagebox')
  console.log("導入Url")
  if(input.files && input.files[0]) {
    let reader = new FileReader();
    reader.onload = function(e) {
      // console.log(e)
      imagebox.attr('src', e.target.result); 
      imagebox.height(500);
      imagebox.width(800);
    }
    reader.readAsDataURL(input.files[0]);
    // Clear the test results
    $('#testresults').html('');
    $('#loading').hide(); // 隱藏讀條
  }
}

function dataURLtoFile(dataurl, filename) {
  var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
      bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
  while(n--){
      u8arr[n] = bstr.charCodeAt(n);
  }
  return new File([u8arr], filename, {type:mime});
}

// **存入歷史紀錄**
function saveHistory(imageUrl, labels, calories) {
  let timestamp = new Date().toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false });
  
  $.ajax({
    url: `${baseURL}/saveHistory`,
    type: "POST",
    data: JSON.stringify({ labels: labels, calories: calories , image_path: imageUrl, timestamp: timestamp}),
    contentType: "application/json",
    success: function(response) {
      console.log("✅ 歷史紀錄已存入 MySQL:", response);
    },
    error: function(xhr, status, error) {
      console.error("❌ 存入歷史紀錄失敗:", error);
    }
  });
}

// **顯示歷史紀錄**
function showHistory(page = 1) {
  $('.HomeContainer').hide();
  $('.historyContainer').fadeIn(500);
  $('.detectFoodContainer').fadeOut(500);

  $.ajax({
    url: `${baseURL}/getHistory`,
    type: "GET",
    success: function(response) {
      if (!response.success) {
        alert("❌ 讀取歷史紀錄失敗：" + response.error);
        return;
      }
      console.log("✅ 讀取歷史紀錄成功:", response);

      let history = response.history;
      if (history.length === 0) {
        $('#historyList').html('<p style="text-align:center;">尚無歷史紀錄</p>');
        $('#paginationInfo, #firstPageButton, #prevPageButton, #nextPageButton, #lastPageButton').hide();
        return;
      }

      // 清空舊內容
      $('#historyList').empty();

      const itemsPerPage = 5;
      const totalPages = Math.ceil(history.length / itemsPerPage);
      const startIndex = (page - 1) * itemsPerPage;
      const endIndex = Math.min(startIndex + itemsPerPage, history.length);

      // **組合 HTML 並插入**
      const historyHTML = history.slice(startIndex, endIndex).map(entry => {
        const foodCalories = entry.labels.length > 0 
          ? entry.labels.map((label, index) => `${label}(${entry.calories[index]} kcal)`).join(', ')
          : "無法辨識此圖片中的食物";

        return `
          <li>
            <img src="${entry.image_path}" width="500px"> 
            <div>
              <h4>食物(熱量): ${foodCalories}</h4>
              <p>${entry.timestamp}</p>
            </div>  
          </li>
        `;
      }).join('');

      $('#historyList').html(historyHTML);

      // **更新頁碼顯示**
      $('#paginationInfo').html(`📄 第 ${page} 頁 / 共 ${totalPages} 頁`).show();

      // **顯示或隱藏分頁按鈕**
      $('#firstPageButton').toggle(page > 2);
      $('#prevPageButton').toggle(page > 1);
      $('#nextPageButton').toggle(page < totalPages);
      $('#lastPageButton').toggle(page < totalPages - 1);

      // **綁定按鈕事件 (先解除舊事件避免累積)**
      $('#firstPageButton').off().on("click", () => showHistory(1));
      $('#prevPageButton').off().on("click", () => showHistory(page - 1));
      $('#nextPageButton').off().on("click", () => showHistory(page + 1));
      $('#lastPageButton').off().on("click", () => showHistory(totalPages));
    },
    error: function(xhr, status, error) {
      console.error("❌ 讀取歷史紀錄失敗:", error);
      alert("讀取歷史紀錄時發生錯誤，請稍後再試！");
    }
  });

  // **清空歷史紀錄**
  $('#clearHistoryButton').off().on("click", () => {
    if (confirm("確定要清空所有歷史紀錄嗎？")) {
      $.ajax({
        url: `${baseURL}/clearHistory`,
        type: "POST",
        success: function(response) {
          if (response.success) {
            $('#historyList').html('<p style="text-align:center;">尚無歷史紀錄</p>');
            $('#paginationInfo, #firstPageButton, #prevPageButton, #nextPageButton, #lastPageButton').hide();
            alert("歷史紀錄已清空！");
          } else {
            alert("❌ 清除失敗：" + response.error);
          }
        },
        error: function(xhr, status, error) {
          console.error("❌ 清除歷史紀錄失敗:", error);
          alert("無法清除歷史紀錄，請稍後再試！");
        }
      });
    }
  });
}

document.addEventListener("click", (event) => {
  if (event.target.classList.contains("deleteHistory")) {
      let index = event.target.dataset.index;
      deleteHistory(index);
  }
});