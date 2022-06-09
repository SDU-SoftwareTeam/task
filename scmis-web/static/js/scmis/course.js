var apiKeys = ['id', 'course_name', 'teacher_username', 'period', 'classroom','end_time', 'description' ,'capacity', 'max_capacity']
var apiKeys1 = ['id', 'course_name', 'capacity', 'max_capacity','period', 'classroom','end_time', 'description']
var apiKeys2 = ['id', 'course_name', 'max_capacity','teacher_username','period','end_time', 'classroom', 'description']
var dataTablesObject = null

$(document).ready(function () {
    $('#table td').css('text-align', 'center')
    $('#table th').css('text-align', 'center')
    $("#btn-Query").on('click', queryClicked)
    $('#btn-Add').on('click', addClicked)
    $("#btn-editcourseConfirm").on('click', addOrEditComfirm)
    $("#btn-addcourseConfirm").on('click', addOrEditComfirm)
    dataTablesObject = initTable('table')
    mydataTablesObject = initTable('mytable')
    studataTablesObject = initTable('stutable')
    studataTablesObject2 = initTable('stutable2')
    $('#mytable').hide()
    $('#show').on('click', function () {
        $('#mytable').show()
        // mydataTablesObject = initTable('mytable')
        querymycourses()
    })
    queryClicked()
})
//load my courses
function querymycourses() {
    var json_data = JSON.stringify({
        "class_name": "",
        "id": "",
        "teacher_name": "",
        "teacher_id": $('#userId').val()
    })
    AJAX({
        url: "/api/course/query",
        type: "POST",
        data: json_data,
        contentType: "application/json",

        success: function (data) {
            if (data.errcode !== '0') {
                alert(data.errmsg)
                if (data.errcode === '4101') {
                    window.location.href = '/'
                }
                return
            }
            if (typeof (mydataTablesObject) !== "undefined" && mydataTablesObject !== null) {
                mydataTablesObject.destroy()
            }
            $('#mytable>tbody tr').remove()
            var tb = $('#mytable>tbody')[0]
            data['data'].forEach(function (value) {
                var tr = tb.insertRow()
                for (var i = 0; i < apiKeys1.length; i++) {
                    var td = tr.insertCell()
                    td.style = "text-align: center;"
                    td.innerHTML = value[apiKeys1[i]]
                    td.setAttribute("value", td.innerHTML)
                }
                var td = tr.insertCell()
                // 判定权限
                if ($('.nav li a').attr('href').indexOf('role=2') === -1) {
                    td.style = "text-align: center;"
                    // 编辑删除
                    td.innerHTML = '<a style="cursor:pointer" onclick="uploadgrade(this)">查看学生/成绩录入</a>'
                }
            })
            mydataTablesObject = initTable('mytable')
        }
    })
}

function seestu2(cid) {
    var json_data = JSON.stringify(
        {
            "student_id": null,
            "course_id": cid
        }
    )
    AJAX({
        url: "/api/take/query",
        type: "POST",
        data: json_data,
        contentType: "application/json",

        success: function (data) {
            if (data.errcode !== '0') {
                alert(data.errmsg)
                if (data.errcode === '4101') {
                    window.location.href = '/'
                }
                return
            }
            if (typeof (studataTablesObject2) !== "undefined" && studataTablesObject2 !== null) {
                studataTablesObject2.destroy()
            }
            $('#stutable2>tbody tr').remove()
            var tb = $('#stutable2>tbody')[0]
            data['data'].forEach(function (value) {
                var tr = tb.insertRow()
                let apiKey = ["student_username", "name", "grade","department","major"]
                for (var i = 0; i < apiKey.length; i++) {
                    var td = tr.insertCell()
                    td.style = "text-align: center;"
                    td.innerHTML = value[apiKey[i]]
                    td.setAttribute("value", td.innerHTML)
                }
            })
            studataTablesObject2 = initTable('stutable2')
        }
    })
}

//uploadgrade
function uploadgrade(v) {
    v = v.parentElement.parentElement.cells
    let course_id = v[0].getAttribute("value")
    $(".uploadgrade").modal()
    $('#btn-gradeadd').on('click', uploadgradeConfirm(course_id))
    seestu2(v[0].getAttribute("value"))
}

function queryStudentInCourse(v) {
    v = v.parentElement.parentElement.cells
    let course_id = v[0].getAttribute("value")
    $(".uploadgrade").modal()
    seestu2(v[0].getAttribute("value"))
    $('#btn-gradeadd').hide()
    $('#div-fileuploader').hide()
}

function uploadgradeConfirm(cid) {

    //上传成绩excel文件录入成绩
    document.querySelector("#gradefile").addEventListener("change", function () {
        //获取到选中的文件
        var file = document.querySelector("#gradefile").files[0];
        var type = file.name.split('.');
        if (type[type.length - 1] !== 'xlsx' && type[type.length - 1] !== 'xls') {
            alert('只能选择excel文件导入');
            return false;
        }
        const reader = new FileReader();
        reader.readAsBinaryString(file);
        reader.onload = (e) => {
            const data = e.target.result;
            const zzexcel = window.XLS.read(data, {
                type: 'binary'
            });
            // console.log(zzexcel)
            const result = [];
            for (let i = 0; i < zzexcel.SheetNames.length; i++) {
                newData1 = window.XLS.utils.sheet_to_json(zzexcel.Sheets[zzexcel.SheetNames[i]], { header: 1, defval: ' ' });//空值用‘’，输出为数组
                //处理成【{coureseid：，grade：}，{}】
                newData1 = newData1.slice(2)
                result1 = []
                newData1.forEach(function (item) {
                    let x = {}
                    x["student_id"] = item[0]
                    x["grade"] = item[2]
					if(item[2] == null) x["grade"] = "";
                    result1.push(x)
                })
            }
            //   console.log(result)
            //格式化
            //   console.log( JSON.stringify(result))
            json_data = JSON.stringify({
                "course_id": cid,
                "details": result1
            })
            $('#btn-gradeadd').on('click', function () {
                AJAX({
                    url: "/api/take/edit",
                    type: "POST",
                    data: json_data,
                    contentType: "application/json",
                    beforeSend: function () {
                        $('#btn-gradeadd').text("提交中...").attr("disabled", true);
                        NProgress.start()
                    },
                    complete: function () {
                        $('#btn-gradeadd').text("确认提交").attr("disabled", false);
                        NProgress.done()
                    },
                    success: function (data) {
                        if (data.errcode === "0") {
                            alert(data.errmsg)
                            seestu2(cid)
                        } else {
                            alert(data.errmsg)
                        }
                    }
                })
                // location.reload();
            })
        }
    });
}

//all courses
function queryClicked() {
    var json_data = JSON.stringify({
        "class_name": $("#courseName").val(),
        "id": $("#courseId").val(),
        "teacher_name": $("#teacherName").val(),
        "teacher_id": null
    })

    AJAX({
        url: "/api/course/query",
        type: "POST",
        data: json_data,
        contentType: "application/json",
        beforeSend: function () {
            NProgress.start()
            $('#btn-Query').text("查询中...").attr("disabled", true)
        },
        complete: function () {
            NProgress.done()
            $('#btn-Query').text("查询课程设置信息").attr("disabled", false)
        },
        success: function (data) {
            if (data.errcode !== '0') {
                alert(data.errmsg)
                if (data.errcode === '4101') {
                    window.location.href = '/'
                }
                return
            }
            if (typeof (dataTablesObject) !== "undefined" && dataTablesObject !== null) {
                dataTablesObject.destroy()
            }
            $('#table>tbody tr').remove()
            var tb = $('#table>tbody')[0]
            data['data'].forEach(function (value) {
                var tr = tb.insertRow()
                for (var i = 0; i < apiKeys.length; i++) {
                    var td = tr.insertCell()
                    td.style = "text-align: center;"
                    td.innerHTML = value[apiKeys[i]]
                    td.setAttribute("value", td.innerHTML)
                    if(apiKeys[i] === 'teacher_username'){
                        td.innerHTML =value['teacher_name']
                    }
                    if(apiKeys[i] === 'end_time'){
                        var date = new Date(value[apiKeys[i]])
                        // console.log(typeof(date));
                        td.setAttribute("value", date)
                    }
                }
                var td = tr.insertCell()
                // 判定权限
                if ($('.nav li a').attr('href').indexOf('role=2') === -1) {
                    td.style = "text-align: center;"
                    // 编辑删除
                    td.innerHTML =
                        '<a style="cursor:pointer" onclick="uploadgrade(this)">查看学生/录入成绩</a>'+
                        '<a style="cursor:pointer" onclick="editClicked(this)">编辑</a> ' +
                        '<a style="cursor:pointer" onclick="deleteClicked(this)">删除</a>'
                }
            })
            dataTablesObject = initTable('table')
        }
    })
}

function addClicked() {
    for (var i = 0; i < apiKeys.length; i++) {
        $("#input-editcourse-" + apiKeys[i]).val("")
    }
    $("#btn-editcourseConfirm").hide()
    $("#btn-addcourseConfirm").show()
    $("#modalTitle").text("课程设置信息 添加")
    $("#editcourseInfoModal").modal()
    $($("#input-editcourse-id")[0].parentElement).hide()
}

function editClicked(v) {
    v = v.parentElement.parentElement.cells
    //默认赋值
    for (var i = 0; i < apiKeys.length; i++) {
        if (apiKeys[i] === 'end_time'){
            var origntime=v[5].innerHTML.replace(' ','T')
            origntime=origntime.substr(0,origntime.length-3)
            $("#input-editcourse-end_time").val(origntime);
        } else{
            $("#input-editcourse-" + apiKeys[i]).val(v[i].getAttribute("value"))
        }
    }
    $("#btn-addcourseConfirm").hide()
    $("#btn-editcourseConfirm").show()
    $($("#input-editcourse-id")[0].parentElement).show()
    $("#modalTitle").text("课程设置信息 修改")
    $("#editcourseInfoModal").modal()
}

function addOrEditComfirm() {
    var data = {}
    for (var i = 0; i < apiKeys2.length; i++) {
        data[apiKeys2[i]] = $("#input-editcourse-" + apiKeys2[i]).val()
    }
    data['end_time']=data['end_time'].replace(/T/gi, ' ')+":00"
    var json_data = JSON.stringify(data)
    if (event.srcElement.id === "btn-editcourseConfirm") {
        AJAX({
            url: "/api/course/edit",
            type: "POST",
            data: json_data,
            contentType: "application/json",
            beforeSend: function () {
                $('#btn-editcourseConfirm').text("修改中...").attr("disabled", true);
                NProgress.start()
            },
            complete: function () {
                $('#btn-editcourseConfirm').text("确认修改").attr("disabled", false);
                NProgress.done()
            },
            success: function (data) {
                if (data.errcode === "0") {
                    location.reload();
                    alert(data.errmsg)
                } else {
                    alert(data.errmsg)
                }
            }
        })
    } else {//缺少接口
        var data = {}
        for (var i = 0; i < apiKeys.length; i++) {
            data[apiKeys[i]] = $("#input-editcourse-" + apiKeys[i]).val()
        }
        var json_data = JSON.stringify(data)
        $.ajax({
            url: "/api/course/add",
            type: "POST",
            data: json_data,
            contentType: "application/json",
            beforeSend: function () {
                $('#btn-addcourseConfirm').text("添加中...").attr("disabled", true);
                NProgress.start()
            },
            complete: function () {
                $('#btn-addcourseConfirm').text("确认添加").attr("disabled", false);
                NProgress.done()
            },
            success: function (data) {
                if (data.errcode === "0") {
                    location.reload();
                    alert(data.errmsg)
                } else {
                    alert(data.errmsg)
                }
            }
        })
    }
}

function deleteClicked(v) {
    // console.log(v.parentElement.parentElement.cells[0].innerHTML)
    if (confirm("确定删除课程信息?")) {
        AJAX({
            url: "/api/course/delete",
            type: "POST",
            data: JSON.stringify({ "id": v.parentElement.parentElement.cells[0].innerHTML }),
            contentType: "application/json",
            beforeSend: function () {
                NProgress.start()
            },
            complete: function () {
                NProgress.done()
            },
            success: function (data) {
                if (data.errcode === "0") {
                    dataTablesObject.row(v.parentElement.parentElement).remove().draw()
                    alert(data.errmsg)
                } else {
                    alert(data.errmsg)
                }
            }
        })
    }
    // console.log(v.parentElement.parentElement.cells[0].innerHTML)

}
//上传 excel文件录入课程
//首先监听input框的变动，选中一个新的文件会触发change事件
document.querySelector("#file").addEventListener("change", function () {
    //获取到选中的文件
    var file = document.querySelector("#file").files[0];
    var type = file.name.split('.');
    if (type[type.length - 1] !== 'xlsx' && type[type.length - 1] !== 'xls') {
        alert('只能选择excel文件导入');
        return false;
    }
    const reader = new FileReader();
    reader.readAsBinaryString(file);
    reader.onload = (e) => {
        const data = e.target.result;
        const zzexcel = window.XLS.read(data, {
            type: 'binary'
        });
        const result = [];
        for (let i = 0; i < zzexcel.SheetNames.length; i++) {
            const newData = window.XLS.utils.sheet_to_json(zzexcel.Sheets[zzexcel.SheetNames[i]]);
            result.push(...newData)
        }
        console.log(result)
        //格式化
        // console.log( JSON.stringify(result))

        $('#btn-Add2').on('click', function () {
            AJAX({
                url: "/api/course/add",
                type: "POST",
                data: JSON.stringify(result),
                contentType: "application/json",
                beforeSend: function () {
                    $('#btn-Add2').text("提交中...").attr("disabled", true);
                    NProgress.start()
                },
                complete: function () {
                    $('#btn-Add2').text("提交成功").attr("disabled", false);
                    NProgress.done()
                },
                success: function (data) {
                    if (data.errcode === "0") {
                        alert(data.errmsg)
                        location.reload();
                    } else {
                        alert(data.errmsg)
                    }
                }
            })
        })

    }
});
