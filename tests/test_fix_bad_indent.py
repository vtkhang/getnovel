from novelutils.utils.file import fix_bad_indent

mylist = [
    'Truyện mới của tác giả Dong Wook Lee là câu chuyện về chuyến phiêu lưu của một chàng trai "vô tài,\nlắm tật" trên bước đường ',
    'chinh phục',
    ' những thành tựu của đời mình.',
    'Và hơn thế nữa, ',
    '[Overgeared] Thợ Rèn Huyền Thoại',
    ' cũng chính là hành trình của một cậu bé gắt gỏng bất mãn với đời, đứa trẻ ích kỷ chỉ biết nghĩ cho bản thân mình. Trở thành\nmột người đàn ông biết lo lắng, thương yêu và tín nhiệm với mọi người\nxung quanh.',
    'Tóm tắt ',
    'truyện huyền huyễn',
    ':',
    'Mang trong người một cuộc đời bất hạnh, Shin Youngwoo bấy giờ phải xúc đất và bốc gạch tại những công trình xây dựng. Cậu thậm chí phải lao động chân tay trong một trò chơi thực tế ảo có tên là Viên Mãn Giới!',
    'Tuy nhiên, vận may du nhập vào cuộc đời vô vọng của Young Woo. Nhân vật Grid của cậu, trong một nhiệm vụ đã phát hiện ra Động Kết Bắc. Trong nơi ấy, Young Woo đã vô tình tìm được "Bảo Thư của Pagma". Và đó là ngày đánh dấu cho sự ra đời của một huyền thoại.',
    '***'
]

m = [x.strip() for x in mylist]
print("\n".join(fix_bad_indent(m)))
