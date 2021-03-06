from datetime import datetime, timedelta, timezone

import jenkins as jenkins


class Jenkins(jenkins.Jenkins):
    def matrix(self, view_name):
        views = self.get_jobs(view_name=view_name)
        return views

    def job_result(self, job):
        """
        Fetches the latest job results from Jenkins for the
        configured job
        """
        job_info = self.get_job_info(job['name'])
        if job_info is None or job_info['lastBuild'] is None:
            return {}
        build_info = self.get_build_info(
            job['name'],
            job_info['lastBuild']['number'],
            depth=1)
        results = {}
        for run in build_info['runs']:
            series = get_series_from_url(run['url'])
            details = result_from_run(run)
            if details is not None:
                results[series] = details
        return results


def result_from_run(run):
    """
    Summarizes a run from Jenkins API

    :param run: Details of the run from Jenkins
    :type dict
    :returns Summary of the run
    :rtype dict
    """
    date = datetime.fromtimestamp(run['timestamp'] / 1000, tz=timezone.utc)
    thirty_days_ago = datetime.now(tz=timezone.utc) - timedelta(days=30)
    if date < thirty_days_ago:
        return
    name_split = run['fullDisplayName'].split(' ')
    success = run['result'] == "SUCCESS"
    if success:
        state = 'Pass'
    else:
        state = 'Fail'
    return {
        'successful': success,
        'state': state,
        'url': run['url'],
        'date': date,
        'name': name_split[0],
        'spec': name_split[-2].split(',')[0],
    }


def get_series_from_url(url):
    """
    Breaks a Jenkins job URL out to retrieve U_OS combination


    :param url: Jenkins job URL
    :type str
    :returns: Ubuntu/OpenStack combination
    :rtype: Option(str)
    """
    if 'U_OS' in url:
        return url.split('U_OS=')[-1].split('/')[0]
