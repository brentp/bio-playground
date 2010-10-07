#include <iostream>
#include <stdlib.h>
#include <fstream>
#include <string.h>
#include <sstream> // for int2strinng
#include <vector>
#include <algorithm> // for count
#include <numeric> // for accumulate
#include <map> // for sorted map.
#include <tr1/unordered_map>
using namespace std;
#define DEFAULT -999

const char *usage = "============================================\n"
    "fastq  : utilities for summarizing and filtering fastq files\n"
    "author : brentp (bpederse@gmail.com)\n"
    "license: MIT\n"
    "\n"
    "usage:\n\t$ fastq [action] [options]\n"
    "where [action] is one of 'summarize' or 'filter':\n"
    "\t$ fastq summarize [summarize_options]\n"
    "      [summarize_options] are:\n"
    "\t--codon : print a codon usage table with columns A,C,T,G,N and one\n"
    "\t\trow per read basepair\n"
    "\t--quality : print a quality table with columns:\n"
    "\t\tmean, std, median, 1, 2.5, 5, 10 , 25, 75, 90, 95, 97.5, 99%\n"
    "\t\tand one row per read-basepair\n"
    "\n"
    "     [filter_options] are\n:"
    "\t--quality [X] mask bases with quality < X to 'N'\n"
    "\t--n [X] exclude records with more than X 'N's (after above masking)\n"
    "\t--unique after above filtering, print only unique sequences\n"
    "\t(for those groups with more than one record, choose the one\n"
    "\t with the best quality\n"
    "\n"
    "both 'summarize' and 'filter' require an additional option:\n"
    "\t--adjust [N] where N is likely either 33 or 64. see:\n"
    "\thttp://en.wikipedia.org/wiki/FASTQ_format\n"
;
void error(const char *msg){
    fprintf(stderr, "**%s\n", msg);
}

typedef struct fastq_record {
    string seq;
    string header;
    string squality;
    string oheader;
    vector<int> iquality;
    float average_quality;
    int ns;
    bool operator< (const fastq_record &b) const{
        return average_quality < b.average_quality;
    };
} fastq_record;

inline void write_fastq_record(fastq_record fq){
    printf("%s\n%s\n%s\n%s\n", 
                    fq.header.c_str(),
                    fq.seq.c_str(),
                    fq.oheader.c_str(),
                    fq.squality.c_str());
}

typedef struct opts {
    string action;
    int adjust;
    bool filter_unique;
    int filter_quality;
    int filter_n;
    bool summarize_codon;
    bool summarize_quality;
    string filename;
} opts;

typedef vector<fastq_record> record_list;

// http://www.cplusplus.com/forum/articles/13355/
// http://www.codeguru.com/cpp/cpp/cpp_mfc/stl/article.php/c15303__2
//typedef std::tr1::unordered_multimap<string, fastq_record> record_multimap;
typedef tr1::unordered_map<string, record_list> record_map;
typedef tr1::unordered_map<char, int> char_int_map;
typedef tr1::unordered_map<int, char_int_map> bp_char_freq_map;

typedef tr1::unordered_map<int, int> int_int_map;
typedef tr1::unordered_map<int, int_int_map> bp_qual_freq_map;

void add_quality(fastq_record *qr, int adjust, int filter_limit, int *masked){
    int l = qr->squality.length();
    qr->iquality.resize(l);
    qr->squality.resize(l);

    for(int i=0; i < l; i++){
        qr->iquality[i] = qr->squality[i] - adjust;
        if(qr->iquality[i] < filter_limit){
            qr->seq[i] = 'N';
            *masked += 1;
        }
    }
    qr->average_quality = accumulate(qr->iquality.begin(), 
                                     qr->iquality.end(), 0) / (float)l;
    
}

string int2string(int number) {
   stringstream ss; //create a stringstream
   ss << number; //add number to the stream
   return ss.str(); //return a string with the contents of the stream
}

int chart_adjust(int nreads){
    return nreads > 10000000 ? 10000 : nreads > 1000000 ? 1000 : nreads > 100000 ? 100 : nreads > 10000 ? 10 : 1;
}


int fsummarize_quality(opts o){
    bp_qual_freq_map quality_map;
    int_int_map imap;
    struct fastq_record qr;
    ifstream fh (o.filename.c_str(), ios::in);
    if (!fh.is_open()){ 
        fprintf(stderr, "does '%s' exist? not able to open\n", 
                o.filename.c_str());
        return 1;
    }
    float _stat_pts[] = {0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99};
    vector<float> stat_pts (_stat_pts, _stat_pts + sizeof(_stat_pts) / sizeof(float));
    vector<float>::iterator stat_it;

    int i, L, nreads=0, masked=0;
    while (!fh.eof()){
        fh >> qr.header;
        fh >> qr.seq;
        fh >> qr.oheader;
        fh >> qr.squality;
        add_quality(&qr, o.adjust, 0, &masked);
        L = qr.iquality.size();
        for(i=0; i < L; ++i){
            // so here we have a lookup of read position -> quality_score -> count.
            quality_map[i][qr.iquality[i]]++; 
        }
        ++nreads;

    }
    long qsum_quality;
    int qi;

    vector<int> counts;
    string url = "http://chart.apis.google.com/chart?chbh=a&chdlp=l&cht=lc&chs=800x300&chco=FF0000,00FF00,0000FF,FFFF00,CCCCCC";
    //url += "&chxt=x,x&chxr=0,1," + int2string(l) + "," + int2string(l - 1) + "&chxl=1:|read position|&chxp=1," + int2string(2 * l / 3);
    url += "&chd=t0:";
    for(i=0; i < L; ++i){
        qsum_quality = 0;
        imap = quality_map[i];
        counts.clear();
        for(int_int_map::const_iterator it=imap.begin(); it != imap.end(); ++it){
            // first is the quality. 2nd is the count.
            qsum_quality += (it->first * it->second);
            // faster way to do this?
            for(qi=0; qi < it->second; qi++){ counts.push_back(it->first); }
        }

        // sort then find the pctiles.
        sort(counts.begin(), counts.end());

        string stats = "";
        for(stat_it=stat_pts.begin(); stat_it != stat_pts.end(); stat_it++){
            stats += int2string(counts[nreads * (*stat_it)]) + "\t"; 
        }

        printf("%i\t%s%.5f\n", i + 1, stats.c_str(), (float)qsum_quality / nreads);
    }
    return 0;
}

int fsummarize_codon(opts o){
    bp_char_freq_map cm;
    struct fastq_record qr;
    ifstream fh (o.filename.c_str(), ios::in);
    if (!fh.is_open()){ 
        fprintf(stderr, "does '%s' exist? not able to open\n", 
                o.filename.c_str());
        return 1;
    }
    // this is o.summarize_codon
    int i, l, si;
    int nreads = 0;
    while (!fh.eof()){
        fh >> qr.header;
        fh >> qr.seq;
        fh >> qr.oheader;
        fh >> qr.squality;
        l = qr.squality.length();
        for(i=0; i < l; ++i){
            // default is 0, so no need to intialize.
            // hash of read position -> char -> count.
            cm[i][qr.seq[i]]++;
        }
        nreads += 1;
    }
    string actgn = "ACGTN";
    string url = "http://chart.apis.google.com/chart?chbh=a&chdl=A|C|G|T|N&chdlp=l&cht=bvs&chs=800x300&chco=FF0000,00FF00,0000FF,FFFF00,CCCCCC";
    url += "&chxt=x,x&chxr=0,1," + int2string(l) + "," + int2string(l - 1) + "&chxl=1:|read position|&chxp=1," + int2string(2 * l / 3);
    int div = chart_adjust(nreads);
    url += "&chds=0," + int2string(nreads/ div + 1) + "&chd=t:";
    printf("#reads: %i\n", nreads);
    for(si=0; si < actgn.size(); si++){
        for (i=0; i < l; ++i){
            int val = cm[i][actgn[si]] / div;
            url += int2string(val) + (i == l - 1 ? "" : ",");
        }
        if(si < actgn.size() -1) {url += "|";}
    }

    printf("#%s\n", url.c_str());
    printf("read_pos\tA\tC\tG\tT\tN\n");
    for (i=0; i < l; ++i){
        printf("%i", i + 1);
        for(si =0; si < actgn.size(); si++){
            int val = cm[i][actgn[si]];
            printf("\t%i", val);
        }
        printf("\n");
    }
    return 1;
}

int write_filtered(record_map &rm, opts &o){
    fprintf(stderr, "in write_filtered\n");
    record_list rl;
    int i;

    for(record_map::const_iterator it = rm.begin(); it != rm.end(); ++it){
        // it->first is the sequence key.
        rl = it->second;
        // only write the one with best avg_q
        if(o.filter_unique){
            // sort by average_quality.
            sort(rl.rbegin(), rl.rend());            
            write_fastq_record(rl[0]);
        }            
        else {
            for(i=0; i < rl.size(); i++){
                write_fastq_record(rl[i]);
            }
        }
    } 
}


int filter(opts o){
    record_map rm;
    struct fastq_record qr;
    int ns_skipped = 0;
    int i = 0;
    int quality_skipped = 0;
    ifstream fh (o.filename.c_str(), ios::in);
    if (!fh.is_open()){ 
        cout << "does '" << o.filename << "' exist? not able to open" << endl;
        return 1;
    }
    record_map::iterator pos;
    while (!fh.eof()){
        i += 1;
        fh >> qr.header;
        fh >> qr.seq;
        fh >> qr.oheader;
        fh >> qr.squality;

        add_quality(&qr, o.adjust, o.filter_quality, &quality_skipped);

        qr.ns = count(qr.seq.begin(), qr.seq.end(), 'N');
        if (qr.ns > o.filter_n){
            ns_skipped += 1;
            continue;
        }
        
        pos = rm.find(qr.seq);
        if (pos == rm.end()){
            // create a new vector.
            vector<fastq_record> rl;
            rl.push_back(qr);
            rm.insert(record_map::value_type(qr.seq, rl));
        }
        else {
            // already seen, add it to the vector.
            rm[qr.seq].push_back(qr);
        }
    }
    fprintf(stderr, "masked %i basepairs because of quality's\n", 
            quality_skipped);
    float ratio = (float)ns_skipped/i * 100.0;
    fprintf(stderr, "skipped %i reads because of N's(%.3f %%)\n", 
            ns_skipped, ratio);

    ratio = (float)rm.size()/i * 100.0;
    fprintf(stderr, "read %i unique of %i total records(%.3f %%)\n",
            (int)rm.size(), i, ratio);
    return write_filtered(rm, o);
}



int parse_args(int argc, char *argv[], opts *o){
    int i;
    o->filter_n = 0;
    o->filter_unique = false;
    o->filter_quality = DEFAULT;
    o->summarize_codon = false;
    o->summarize_quality = false;
    o->adjust = DEFAULT;
    o->action = (string)argv[1];
    o->filename = (string)argv[argc - 1];
    
    if(o->action == "summarize"){
        for(i=2; i < argc - 1;){
            if(string(argv[i]) == "--codon"){
                o->summarize_codon = true;
            }
            else if (string(argv[i]) == "--quality"){
                o->summarize_quality = true;
            }
            else if (string(argv[i]) == "--adjust"){
                o->adjust = atoi(argv[i + 1]);
                i += 1;
            }
            else {
                fprintf(stderr, "bad argument: %s\n", argv[i]);
            }
            i++; 
        }
    }
    //bool filter_unique;
    //int filter_quality;
    else if (o->action == "filter"){
        for(i=2; i < argc - 1;){
            if(string(argv[i]) == "--unique"){
                o->filter_unique = true;
            }
            else if (string(argv[i]) == "--adjust"){
                o->adjust = atoi(argv[i + 1]);
                i += 1;
            }
            else if (string(argv[i]) == "--quality"){
                o->filter_quality = atoi(argv[i + 1]);
                i += 1;
            }
            else if (string(argv[i]) == "--n"){
                o->filter_n = atoi(argv[i + 1]);
                i += 1;
            }
            else {
                fprintf(stderr, "bad argument: %s\n", argv[i]);
            }
            i++;
        }

    }
    else {
        return 1;
    }
    if(o->adjust == -999 && o->filter_quality != DEFAULT && o->action == "filter"){
        error("must send in value for --adjust");
        return 1;
    }
    return 0;
}

int main(int argc, char *argv[]){
    if (argc < 3){
        error(usage);
        return 1;
    }
    opts o;
    if(parse_args(argc, argv, &o) != 0){
        error(usage);
        return 1;
    }

    record_map rm;

    if (o.action == "filter"){
        filter(o);
    }
    else if (o.action == "summarize"){
        if (o.summarize_codon){ fsummarize_codon(o); }
        if (o.summarize_quality) { fsummarize_quality(o); }
    }

    return 0;
}

