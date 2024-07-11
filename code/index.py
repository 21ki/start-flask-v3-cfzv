from flask import Flask, request, jsonify
import arrow
import chinese_calendar as cc
from datetime import datetime
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
def get_cst_time():
    """
    获取并转换服务器当前时间为中国标准时间（CST）。
    """
    local_time = datetime.now()  # 获取系统本地时间
    cst_timezone = pytz.timezone('Asia/Shanghai')  # CST 时区为中国标准时间
    cst_time = local_time.astimezone(cst_timezone)  # 将本地时间转换为 CST 时间
    return cst_time

@app.route('/api/is_workday', methods=['GET', 'POST'])
def is_workday():
    if request.method == 'GET':
        date_str = request.args.get('date')
    elif request.method == 'POST':
        data = request.get_json()
        date_str = data.get('date') if data else None

    # 获取服务器当前时间并转换成 CST
    server_time = get_cst_time().date()

    # 如果没有提供日期参数，则使用服务器当前时间
    if not date_str:
        date = server_time
    else:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    is_workday = cc.is_workday(date)
    return jsonify({
        "date": date.isoformat(),
        "is_workday": is_workday
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
