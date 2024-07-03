from flask import Flask, request, jsonify
import arrow
import chinese_calendar as cc
import datetime
import pytz

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def hello_world(path):
    requestId = request.headers.get("x-fc-request-id")
    print("FC Invoke Start RequestId: " + requestId)

    response = jsonify(
        {
            "msg": "Hello, World!" + " at " + arrow.now().format("YYYY-MM-DD HH:mm:ss"),
            "request": {
                "query": str(request.query_string, "utf-8"),
                "path": path,
                "data": str(request.stream.read(), "utf-8"),
                "clientIp": request.headers.get("x-forwarded-for"),
            },
        }
    )

    print("FC Invoke End RequestId: " + requestId)
    return response

@app.route('/api/is_workday', methods=['GET', 'POST'])
def is_workday():
    date_str = None
    if request.method == 'POST':
        if request.data:
            try:
                data = request.get_json()
                date_str = data.get('date')
            except:
                return jsonify({"error": "Invalid JSON data"}), 400
    else:  # GET request
        date_str = request.args.get('date')

    # 获取服务器当前时间并转换成 CST
    server_timezone = pytz.timezone('America/New_York')  # 服务器时区为美国东部时区
    cst_timezone = pytz.timezone('Asia/Shanghai')  # CST 时区为中国标准时间
    server_time = datetime.datetime.now(server_timezone).astimezone(cst_timezone).date()

    # 如果没有提供日期参数，则使用服务器当前时间
    if not date_str:
        date = server_time
    else:
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    is_workday = cc.is_workday(date)
    
    # 调试语句，确认日期是否正确转换成中国时区
    print("Server date and time in CST (China Standard Time):", datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('Asia/Shanghai')))

    return jsonify({
        "date": date.isoformat(),
        "is_workday": is_workday
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
