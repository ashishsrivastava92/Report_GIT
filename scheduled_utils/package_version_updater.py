import time
import requests as git_request
from git_lookup.models import Packages, Repo
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging


def package_version_updater():
    repository = Repo.objects.all()
    logging.basicConfig(filename='logger/scheduler_log.txt', level=logging.INFO)
    cur_time = datetime.now()

    for repo in repository:
        packages = repo.package.all()
        for i in packages:
            if i.updated_at + timedelta(hours=24) < cur_time:
                path = 'package.json'

                url = 'https://api.github.com/repos/{0}/{1}/contents/{2}'.format(repo.owner, repo.repo_name, path)
                try:
                    result = git_request.get(url)
                except git_request.exceptions.RequestException as e:
                    from traceback import format_exc
                    pass
                else:
                    if result.status_code == 200:
                        result = result.json()
                        content = result['content']
                        from base64 import b64decode
                        from ast import literal_eval
                        decoded_content = b64decode(content)
                        decoded_content = decoded_content.replace('\n', '')
                        decoded_content = literal_eval(decoded_content)
                        dependencies = decoded_content['dependencies']
                        all_packages = dependencies.keys()
                        if i.name not in all_packages:      # To check if the package is removed from package.json
                            repo.package.remove(i)
                            continue
                        for pack, ver in dependencies.iteritems():
                            try:
                                package = Packages.objects.get(name=pack)
                                old_version = package.version
                                updated_version = ver
                                for ch in ['&', '#', '-', '.']:
                                    if ch in old_version:
                                        old_version = old_version.replace(ch, '')
                                    if ch in updated_version:
                                        updated_version = updated_version.replace(ch, '')
                                if int(old_version) < int(updated_version):
                                    package.version = ver
                                    package.save()
                                if package.id not in [i.id for i in repo.package.all()]:    # New package
                                    package.count += 1
                                    package.save()
                                    repo.package.add(package)
                                    repo.save()
                            except Packages.DoesNotExist:
                                package = Packages.objects.create(name=pack, version=ver)
                                repo.package.add(package)
                                repo.save()
    return


def scheduler():
    sched = BackgroundScheduler()
    sched.add_job(package_version_updater, 'interval', days=1)
    sched.start()


if __name__ == '__main__':
    scheduler()
    while True:
        time.sleep(0)