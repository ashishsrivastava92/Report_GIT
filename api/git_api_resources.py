import logging
import requests as git_request

from git_lookup.models import Packages, Repo
from api_utils import HttpJsonResponse, dict2obj
from tastypie.http import HttpCreated
from tastypie.resources import Resource

logger = logging.getLogger(__name__)


class GitSearchResource(Resource):
    class Meta:
        resource_name = 'search'
        allowed_methods = ['get']
        object_class = dict2obj

    def obj_get_list(self, bundle, **kwargs):
        get_data = bundle.request.GET.get('q', None)
        limit = bundle.request.GET.get('limit', None)
        offset = bundle.request.GET.get('offset', 0)

        if not get_data:
            response = {'result': 0, 'message': 'Query string missing.'}
            return HttpJsonResponse(HttpCreated, response)
        url = 'https://api.github.com/search/repositories?q={0}'.format(get_data)
        try:
            content = git_request.get(url)
        except git_request.exceptions.RequestException:
            from traceback import format_exc
            logger.error(format_exc())
            response = {'result': 0, 'message': format_exc().splitlines()[-1]}
            return HttpJsonResponse(HttpCreated, response)
        else:
            try:
                if content.status_code == 200:
                    content = content.json()
                    final_content = list()
                    if content['total_count']:
                        for data in content['items']:
                            git_repo = {'repositoryName': data['name'],
                                        'owner': data['owner']['login'],
                                        'starCount': data['stargazers_count'], 'forkCount': data['forks_count']}
                            final_content.append(git_repo)
                        if not limit:
                            limit = 10
                        data = final_content[offset:limit]
                        response = {'result': 1, 'data': data}
                    else:
                        response = {'result': 0, 'message': 'No results found.'}
                else:
                    response = {'result': 0, 'message': 'Request cannot be processed'}
            except Exception as e:
                from traceback import format_exc
                logger.critical(format_exc())
                response = {'result': 0, 'message': 'Request could not be processed.'}
            return HttpJsonResponse(HttpCreated, response)


class GitImportResource(Resource):
    class Meta:
        resource_name = 'import'
        allowed_methods = ['post']
        object_class = dict2obj

    def obj_create(self, bundle, **kwargs):
        post_data = bundle.data
        owner = post_data['owner']
        repo = post_data['repo']
        path = 'package.json'

        url = 'https://api.github.com/repos/{0}/{1}/contents/{2}'.format(owner, repo, path)
        try:
            result = git_request.get(url)
        except git_request.exceptions.RequestException:
            from traceback import format_exc
            logger.error(format_exc())
            response = {'result': 0, 'message': format_exc().splitlines()[-1]}
            return HttpJsonResponse(HttpCreated, response)
        else:
            try:
                if result.status_code == 200:
                    result = result.json()
                    content = result['content']
                    from base64 import b64decode
                    from ast import literal_eval
                    decoded_content = b64decode(content)
                    decoded_content = decoded_content.replace('\n', '')
                    decoded_content = literal_eval(decoded_content)
                    dependencies = decoded_content['dependencies']
                    status, repo = Repo.objects.get_or_create(repo_name=repo, owner=owner)
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
                            if package.id not in [i.id for i in repo.package.all()]:
                                repo.package.add(package)
                                package.count += 1
                                package.save()
                                repo.save()
                        except Packages.DoesNotExist:
                            package = Packages.objects.create(name=pack, version=ver)
                            repo.package.add(package)
                            repo.save()
                    count_packages = len(dependencies.keys())
                    response = {'result': 1, 'count': count_packages}
                else:
                    response = {'result': 0, 'message': 'Request could not be processed.'}
            except Exception as e:
                from traceback import format_exc
                logger.critical(format_exc())
                response = {'result': 0, 'message': 'Request could not be processed.'}
            return HttpJsonResponse(HttpCreated, response)


class GitTopPackCountResource(Resource):
    class Meta:
        resource_name = 'toppacks'
        allowed_methods = ['get']
        object_class = dict2obj

    def obj_get_list(self, bundle, **kwargs):
        import ipdb; ipdb.set_trace()
        count = bundle.request.GET.get('count', None)
        if not count:
            response = {'result': 0, 'message': 'Provide a count value'}
        else:
            packages = Packages.objects.filter(count__gt=int(count)-1)
            if packages:
                data = [i.name for i in packages]
                response = {'result': 1, 'data': data}
            else:
                response = {'result': 0, 'message': 'No package with that much usage count.'}
        return HttpJsonResponse(HttpCreated, response)


class GitPullRequestsResource(Resource):
    class Meta:
        resource_name = 'pullrequests'
        allowed_methods = ['get']
        object_class = dict2obj

    def obj_get_list(self, bundle, **kwargs):
        owner = bundle.request.GET.get('owner', None)
        repo = bundle.request.GET.get('repository', None)
        status = bundle.request.GET.get('status', None)
        if not status:
            status = 'all'

        if owner and repo and status:
            try:
                url = 'https://api.github.com/repos/{0}/{1}/pulls?state={2}'.format(owner, repo, status)
                result = git_request.get(url)
            except git_request.exceptions.RequestException:
                from traceback import format_exc
                logger.error(format_exc())
                response = {'result': 0, 'message': format_exc().splitlines()[-1]}
                return HttpJsonResponse(HttpCreated, response)
            else:
                try:
                    if result.status_code == 200:
                        pull_requests = list()
                        content = result.json()
                        for _data in content:
                            data = {'pullRequestNumber': _data['number'], 'description': _data['body'],
                                    'raisedByUser': _data['user']['login']}
                            if _data['merged_at']:
                                data.update(mergedAt=_data['merged_at'])
                            else:
                                if _data['state'] != 'open':
                                    data.update(status=_data['state'])
                            if _data['state'] == 'open':
                                data.update(openSinceDate=_data['created_at'])
                            pull_requests.append(data)
                        response = {'result': 1, 'pull_requests': pull_requests}
                    else:
                        response = {'result': 0, 'message': 'Request cannot be processed.'}
                except Exception as e:
                    from traceback import format_exc
                    logger.critical(format_exc())
                    response = {'result': 0, 'message': 'Request could not be processed.'}
        else:
            response = {'result': 0, 'message': 'Please provide repository and status. Status are : open, close'
                                                'all'}
        return HttpJsonResponse(HttpCreated, response)






