#!/usr/bin/python

import requests
import json
import os
import pandas as pd

GNPS_SERVER_URL = "gnps.ucsd.edu"
#GNPS_SERVER_URL = "proteomics3.ucsd.edu"

#Returns the library spectra as a list
def pulldown_library(library_name):
    SERVER_URL = "http://%s/ProteoSAFe/LibraryServlet?library=" % (GNPS_SERVER_URL)
    target_url = SERVER_URL + library_name
    r = requests.get(target_url)
    json_text = r.text
    spectra_object = json.loads(json_text)

    return spectra_object["spectra"]

def pulldown_all_continuous_libraries():
    library_names = ["all", "NIST14", "MASSBANK", "MONA", "MASSBANKEU", "HMDB", "RESPECT"]

    library_spectra = []
    for library_name in library_names:
        print("Pulling " + library_name)
        library_spectra += pulldown_library(library_name)

    return library_spectra

#returns specturm
def get_library_spectrum(spectrum_id):
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/SpectrumCommentServlet?SpectrumID="
    url = SERVER_URL + spectrum_id
    r = requests.get(url)
    spectrum_object = json.loads(r.text)

    return spectrum_object


#Returns all datasets as a list of dataset objects
def get_all_datasets(gnps_only=False):
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/datasets_json.jsp"

    url = SERVER_URL
    r = requests.get(url)
    json_object = json.loads(r.text)

    if gnps_only == True:
        gnps_datasets = [dataset for dataset in json_object["datasets"] if dataset["title"].upper().find("GNPS") != -1]
        return gnps_datasets

    return json_object["datasets"];

#Getting all the jobs for a particular dataset in a list
def get_continuous_id_jobs(dataset_task):
    SERVER_URL = "http://gnps.ucsd.edu/ProteoSAFe/ContinuousIDServlet?task="

    url = SERVER_URL + dataset_task
    r = requests.get(url)
    json_object = json.loads(r.text)

    return json_object["jobs"]

def get_dataset_current_continuous_identifications(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    if len(all_jobs) == 0:
        return []
    most_recent_job = all_jobs[0]

    if most_recent_job["workflowname"] == "MOLECULAR-CONTINUOUS-ID":
        #identifications_url = "https://gnps.ucsd.edu/ProteoSAFe/result_json.jsp?task=%s&view=group_by_spectrum_all_beta" % (most_recent_job["task"])
        #dataset_identifications = requests.get(identifications_url).json()["blockData"]

        """New Pandas Method"""
        temp_folder = "temp"
        try:
            os.mkdir(temp_folder)
        except:
            x = 1

        try:
            data_url = "https://%s/ProteoSAFe/DownloadResultFile?task=%s&file=%s" % (GNPS_SERVER_URL, most_recent_job["task"], "DB_result/")
            temp_filename = os.path.join(temp_folder, "%s_DB_result.tsv" % (dataset_task))
            open(temp_filename, "w").write(requests.get(data_url).text.encode('utf-8'))
            df = pd.read_csv(temp_filename, sep="\t")
            dataset_identifications = df.to_dict(orient="records")

            for identification in dataset_identifications:
                identification["task"] = most_recent_job["task"]

            return dataset_identifications
        except KeyboardInterrupt:
            raise
        except:
            print("error", data_url)
            return []

    return []

def get_dataset_current_continuous_pairs(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    if len(all_jobs) == 0:
        return []
    most_recent_job = all_jobs[0]

    if most_recent_job["workflowname"] == "MOLECULAR-CONTINUOUS-ID":
        #pairs_url = "https://%s/ProteoSAFe/result_json.jsp?task=%s&view=clusters_network_pairs" % (GNPS_SERVER_URL, most_recent_job["task"])
        #dataset_pairs = requests.get(pairs_url).json()["blockData"]

        """New Pandas Method"""
        temp_folder = "temp"
        try:
            os.mkdir(temp_folder)
        except KeyboardInterrupt:
            raise
        except:
            x = 1
        data_url = "https://%s/ProteoSAFe/DownloadResultFile?task=%s&file=%s" % (GNPS_SERVER_URL, most_recent_job["task"], "network_edges_withIDs/")
        temp_filename = os.path.join(temp_folder, "%s_edges.tsv" % (dataset_task))
        open(temp_filename, "w").write(requests.get(data_url).text.encode('utf-8'))
        df = pd.read_csv(temp_filename, sep="\t")
        return df.to_dict(orient="records")

    return []

def get_dataset_current_continuous_clustersummary(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    if len(all_jobs) == 0:
        return []
    most_recent_job = all_jobs[0]

    if most_recent_job["workflowname"] == "MOLECULAR-CONTINUOUS-ID":
        """Old Method"""
        #data_url = "https://gnps.ucsd.edu/ProteoSAFe/result_json.jsp?task=%s&view=view_all_clusters_withID" % (most_recent_job["task"])
        #data_list = requests.get(data_url).json()["blockData"]

        #return data_list

        """New Pandas Method"""
        temp_folder = "temp"
        try:
            os.mkdir(temp_folder)
        except KeyboardInterrupt:
            raise
        except:
            x = 1
        data_url = "https://%s/ProteoSAFe/DownloadResultFile?task=%s&file=%s" % (GNPS_SERVER_URL, most_recent_job["task"], "clusterinfosummarygroup_attributes_withIDs/")
        temp_filename = os.path.join(temp_folder, "%s_clusterinfosummarygroup_attributes_withIDs.tsv" % (dataset_task))
        open(temp_filename, "w").write(requests.get(data_url).text.encode('utf-8'))
        df = pd.read_csv(temp_filename, sep="\t")
        return df.to_dict(orient="records")

    return []


#Get the most recent networking job for this dataset
def get_most_recent_continuous_networking_of_dataset(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    #Assume sorted in reverse chronological ordering
    for job in all_jobs:
        if job["workflowname"] == "METABOLOMICS-SNETS":
            return job

    return None

def get_most_recent_reported_continuous_task(dataset_task):
    jobs = get_valid_continous_id_jobs(dataset_task)
    for job in jobs:
        if job["reported"] == "1":
            return job["task"]
    return "NONE"

#Valid defined as the continuous identification jobs since most recent networking
def get_valid_continous_id_jobs(dataset_task):
    all_jobs = get_continuous_id_jobs(dataset_task)
    return_jobs = []
    #Assume sorted in reverse chronological ordering
    for job in all_jobs:
        if job["workflowname"] == "METABOLOMICS-SNETS":
            return return_jobs
        return_jobs.append(job)

    return return_jobs

#Get dataset information with credentials
def get_dataset_information(dataset_task, username, password):

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + "gnps.ucsd.edu" + '/ProteoSAFe/user/login.jsp', data=payload)

    ENDPOINT_URL = "https://gnps.ucsd.edu/ProteoSAFe/MassiveServlet?task=" + dataset_task + "&function=massiveinformation"

    r = s.get(ENDPOINT_URL)
    return json.loads(r.text)


def add_continuous_job(task_id, massive_id, username, password):
    base_url = "gnps.ucsd.edu"

    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + base_url + '/ProteoSAFe/user/login.jsp', data=payload)
    r = s.post('https://' + base_url + '/ProteoSAFe/ContinuousIDServlet?function=addcontinuous&' + "task=" + task_id + "&massive_id=" + massive_id)


def subscribe_dataset(dataset_task, username, password):
    s = requests.Session()

    payload = {
        'user' : username,
        'password' : password,
        'login' : 'Sign in'
    }

    r = s.post('https://' + "gnps.ucsd.edu" + '/ProteoSAFe/user/login.jsp', data=payload, verify=False)
    url = "https://gnps.ucsd.edu/ProteoSAFe/MassiveServlet?task=%s&function=subscription" % (dataset_task)
    s.post(url)
