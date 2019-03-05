# Phát hiện chuyển động sử dụng máy tính nhúng Raspberry Pi và USB camera.

Hầu hết các camera thông minh trên thị trường đều có chức năng phát hiện chuyển động, liệu chúng ta có thể mô phỏng chức năng này với USB camera thông thường sử dụng máy tính nhúng khá phổ biến là Raspberry Pi hay không. Hôm nay mình xin chia sẽ với các ace một phương pháp đơn giản để hiện thực hóa điều này. 

## Yêu cầu

- Raspberry Pi 3

![final-result](./pictures/raspberry_pi3.jpg?raw=true)

- USB Camera

![final-result](./pictures/usb_camera.jpg?raw=true)

- AWS Account

![final-result](./pictures/aws.png?raw=true)

- Biết một ít ngôn ngữ python

![final-result](./pictures/python.png?raw=true)

## Kiến trúc và nguyên lý hoạt động

Hệ thống sẽ gồm các thành phần cơ bản được ghép nối như sau:

![final-result](./pictures/architect.png?raw=true)

Dầu ra hình ảnh từ camera sẽ được đưa vào chương trình xử lý. Chương trình này so sánh sự khác nhau giữa các điểm ảnh trong từng frame và dựa vào một số giá trị ngưỡng để đưa ra kết luận là có chuyển hay không.

Nếu phát hiện chuyển động, nó sẽ phát ra các sự kiện kích hoạt các chương trình khác thực hiện. Tần số xuất hiện của các sự kiện phụ thuộc vào số khung hình (frame) mà camera thu nhận (capture) trong một giây. Do đó, để tránh việc thu nhận quá nhiều sự kiện tương tự nhau, chúng ta sẽ xây dựng một chương trình phụ để lọc các sự kiện này theo thời gian. Ở đây mình đạt gía trị mặt định lầ 5 giây. Nghĩa là nếu có chuyển động thì cứ mỗi 5 giây mới thực hiện cảnh báo một lần.

Việc cảnh báo sẽ được một chương trình thứ ba thực hiện. Chương trình này sử dụng thư viện **boto3** gọi đến service SES của Amazon Web Services để thực hiện gửi mail cho người dùng. Lưu ý rằng email này cần phải được xác thực bởi AWS thì việc gửi mail mới thành công nha.

Toàn bộ hướng dẫn chi tiết có thể tìm thấy tại [đây](https://github.com/IoT-engineer/motion-detection)

## Sử dụng

Các bạn lần lượt chạy các câu lệnh sau để thu được thành quả nhé:

- `sudo motion -c /path/to/motion/config.conf`
- `python filter_event.py`
- `python send_email.py`

Sau đỏ mở trình duyệt lên, gõ vào địa chỉ IP của Rasp, các bạn sẽ thấy được live video từ camera

![dirty-hand](./pictures/sample-01.png?raw=true)

Thực hiện một số chuyển động trước camera sau đó check hộp thư đến, bạn sẽ nhận được cảnh báo qua email

![sample-email](./pictures/sample-email.png?raw=true)

## Kết luận

Như vậy, bạn đã setup thành công một hệ thống phát hiện chuyển động đơn giản. Lần tới mình sẽ sử dụng các service khác của AWS giúp phát hiện người/vật nhằm nâng cao khả năng của hệ thống. 

Cảm ơn các bạn đã đọc bài!
Chúc thành công.