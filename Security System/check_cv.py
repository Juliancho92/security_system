import cv2
print('cv2 version', cv2.__version__)
backends = [('DSHOW', cv2.CAP_DSHOW), ('MSMF', cv2.CAP_MSMF), ('FFMPEG', cv2.CAP_FFMPEG)]
for name, backend in backends:
    print('backend', name)
    for i in range(3):
        cap = cv2.VideoCapture(i, backend)
        print(' index', i, 'opened', cap.isOpened())
        if cap.isOpened():
            ret, frame = cap.read()
            print('  read', ret)
        if cap is not None:
            cap.release()
