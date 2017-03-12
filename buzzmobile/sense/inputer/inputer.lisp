(in-package :buzzmobile)

(defun inputer ()
    (with-ros-node ("inputer")
        (let ((i 0) (pub (advertise "destination" "std_msgs/String")))
            (loop-at-most-every .1
                (publish-msg pub :data (read))))))
