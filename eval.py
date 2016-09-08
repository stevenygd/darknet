import os
import progressbar

DARKNET_HOME = "/workspace/darknet/"

def run_recall(cfg, model, output, thresh, iou_thresh, only_obj = False):
    cmd = " %s yolo recall " % os.path.join(DARKNET_HOME, "darknet")  \
        + " %s "             % os.path.join(DARKNET_HOME, "cfg", cfg) \
        + " %s "             % model  \
        + " -thresh %s "     % thresh \
        + " -iou_thresh %s " % iou_thresh \
        + " -only_obj %s "   % (1 if only_obj else 0) \
        + " >  %s.log "      % output \
        + " 2> %s.err "      % output
    print(cmd)
    os.system(cmd)

if __name__ == "__main__" : 
    model = "/data/yolo_models/model_1/yolo_final.weights"
    cfg   = "yolo.cfg"
    thresh_num = 10
    iou_num    = 10

    # pbar = progressbar.ProgressBar(maxval=(thresh_num * iou_num))
    for i in range(thresh_num):
        thresh = 1./float(thresh_num) * i
        for j in range(iou_num):
            iou = 1./float(iou_num) * j
            print("Thresh:%s, IOU thresh:%s" % (thresh, iou))
            run_recall(cfg, model, "%s/thresh%s_iou%s_out" % ("output_only_obj", thresh, iou) , thresh, iou, True)
            run_recall(cfg, model, "%s/thresh%s_iou%s_out" % ("output", thresh, iou) , thresh, iou, False)
            # pbar.update(i*iou_num+j)
