;;TODO figure out how to import custom messages, specifically buzzmobile.msg.CarPose, buzzmobile.msg.CarState
;;TODO publish the result of mux
;;TODO document the heck out of this (thanks jay)
(in-package :buzzmobile)
(setq globals '((manual_car_pose . NIL) (auto_car_pose . NIL) (curr_car_state . NIL)))

(defun mux (car_state)
    (if (eq car_state 'START) (return NIL)
        (if (eq car_state 'AUTO) (return (cdr (assoc 'auto_car_pose globals)))
        (if (eq car_state 'MANUAL) (return (cdr (assoc 'manual_car_pose globals))) ()))))

(defun set_manual_car_pose (car_pose)
    ((add-to-list 'globals '(manual_car_pose car_pose)) (publish))

(defun set_auto_car_pose (car_pose)
    ((add-to-list 'globals '(auto_car_pose car_pose)) (publish))

(defun set_car_state(car_pose)
    ((add-to-list 'globals '(curr_car_state car_pose)) (publish))

(defun publish () )

(defun car_pose_mux_model ()
    (with-ros-node ("car_pose" :spin t)
        ((subscribe "manual_car_pose" 'CarPose #'set_manual_car_pose)
         (subscribe "auto_car_pose" 'CarPose #'set_auto_car_pose)
         (subscribe "car_state" 'CarPose #'set_car_state))))
