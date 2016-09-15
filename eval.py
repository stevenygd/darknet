import os
import time
import progressbar

DARKNET_HOME = "/workspace/darknet/"

def run_recall(cfg, model, output, thresh, iou_thresh, nms, only_obj = False):
    if nms < 1e-5:
        nms = 0
    if not os.path.isfile("%s.log" % output): # Ignore the case when the file is already created
        cmd = " %s yolo recall " % os.path.join(DARKNET_HOME, "darknet")  \
            + " %s "             % os.path.join(DARKNET_HOME, "cfg", cfg) \
            + " %s "             % model  \
            + " -thresh %s "     % thresh \
            + " -iou_thresh %s " % iou_thresh \
            + " -nms %s "        % nms \
            + " -only_obj %s "   % (1 if only_obj else 0) \
            + " >  %s.log "      % output \
            + " 2> %s.err "      % output
        # print(cmd)
        os.system(cmd)

def parse_last_line(line):
    """
    input is seomthing like:
      100   100	RPs/Img: 625.52	IOU: 39.01%	Prob:0.00029	Recall:100.00%	Precision:0.04%
    output        =  {
        iou       : <iou float>,
        prob      : <prob float>,
        recall    : <recall float>,
        precision : <precision float>
    }
    """
    iou       = float(line[line.index('IOU:') + len("IOU:"):line.index("Prob:")].strip()[:-1]) / float(100)
    prob      = float(line[line.index('Prob:') + len("Prob:"):line.index("Recall:")].strip())
    recall    = float(line[line.index('Recall:') + len("Recall:"):line.index("Precision:")].strip()[:-1]) / float(100)
    precision = float(line[line.index('Precision:') + len("Precision:"):].strip()[:-1]) / float(100)
    return {
        "iou"       : iou,
        "prob"      : prob,
        "recall"    : recall,
        "precision" : precision
    }

if __name__ == "__main__" : 
    # model = "/data/yolo_models/model_1/yolo_final.weights"
    # model = "backup/yolo_adjust_8640_0.001000.weights"
    model_path = "/storage/yolo_models/yolo_orig/"
    # cfg   = "yolo_adjust_test.cfg"
    cfg        = "yolo_te.cfg"
    thresh_num = 20
    iou_num    = 10
    nms_num    = 10

    # pbar = progressbar.ProgressBar(maxval=(thresh_num * iou_num))
    iou = 0
    for model in os.listdir(model_path):
        if not model.endswith(".weights") : continue
        model_p = os.path.join(model_path, model)

        output_obj_only = "%s_output_only_obj" % model
        os.system("mkdir -p %s" % output_obj_only)

        output = "%s_output" % model
        os.system("mkdir -p %s" % output)

        print model, model_p

        recall_obj_only = 0
        precision_obj_only = 0 
        recall_kway = 0 
        precision_kway = 0 
        prev_recall_obj_only = 0
        prev_precision_obj_only = 0 
        prev_recall_kway = 0 
        prev_precision_kway = 0 
        for i in range(thresh_num):
            thresh = .2/float(thresh_num) * i

            for j in range(nms_num):
                nms = 1./float(nms_num) * j

                # print("Thresh:%s, IOU thresh:%s" % (thresh, iou))
                print("Thresh:%s, NMS thresh:%s" % (thresh, nms))

                # run_recall(cfg, model, "%s/thresh%s_iou%s_out" % ("output_only_obj", thresh, iou) , thresh, iou, True)
                # run_recall(cfg, model, "%s/thresh%s_iou%s_out" % ("output", thresh, iou) , thresh, iou, False)

                full_output = "%s/thresh%s_nms%s_out" % (output_obj_only, thresh, nms) 
                run_recall(cfg, model_p, full_output, thresh, iou, nms, True)
                with open('%s.err' % full_output) as f:
                    last = [i for i in f.read().split('\n') if i][-1]
                    parsed = parse_last_line(last)
                    recall_obj_only = parsed["recall"]
                    precision_obj_only = parsed["precision"]
                os.system("cat %s.err | tail -n 1" % full_output)
                print "Obj only:    recall : %f     precision : %f" % (recall_obj_only, precision_obj_only)

                full_output = "%s/thresh%s_nms%s_out" % (output, thresh, nms) 
                run_recall(cfg, model_p, full_output, thresh, iou, nms, False)
                with open('%s.err' % full_output) as f:
                    last = [i for i in f.read().split('\n') if i][-1]
                    parsed = parse_last_line(last)
                    recall_kway = parsed["recall"]
                    precision_kway = parsed["precision"]
                os.system("cat %s.err | tail -n 1" % full_output)
                print "K-way:    recall : %f     precision : %f" % (recall_kway, precision_kway)

                if recall_kway < 10e-5 and recall_obj_only < 10e-5:
                    break
               
                if prev_recall_obj_only == recall_obj_only and prev_recall_kway == recall_kway:
                    break

                prev_recall_obj_only = recall_obj_only
                prev_precision_obj_only = precision_obj_only
                prev_recall_kway = recall_kway
                prev_precision_kway = precision_kway
                time.sleep(0.1)

            if recall_kway < 10e-5 and recall_obj_only < 10e-5:
                break

