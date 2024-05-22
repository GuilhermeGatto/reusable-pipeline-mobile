import sys
import re
import requests

def validate_pr_title(title):
    # Example: PR title must start with a feat ticket ID (e.g., "feat-1234: ")
    pattern = r'^feat-\d+: .+'
    if not re.match(pattern, title):
        return False, 'PR title must start with a feat ticket ID (e.g., "feat-1234: Your title")'
    return True, ''

def validate_labels(labels):
    # Example: PR must have 'bug' or 'feature' label
    required_labels = {'bug', 'feature'}
    if not required_labels.intersection(labels):
        return False, 'PR must have one of the required labels: bug, feature'
    return True, ''

def post_comment(repo, pr_number, message, token):
    comment_url = f'https://api.github.com/repos/{repo}/issues/{pr_number}/comments'
    headers = {'Authorization': f'token {token}'}
    data = {'body': message}
    response = requests.post(comment_url, headers=headers, json=data)
    if response.status_code != 201:
        print(f'Failed to post comment: {response.json()}')
        sys.exit(1)

def main():
    pr_number = sys.argv[1]
    repo = sys.argv[2]
    token = sys.argv[3]

    headers = {'Authorization': f'token {token}'}
    pr_url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}'

    response = requests.get(pr_url, headers=headers)
    pr_data = response.json()

    title = pr_data['title']
    labels = [label['name'] for label in pr_data['labels']]

    title_valid, title_msg = validate_pr_title(title)
    labels_valid, labels_msg = validate_labels(labels)

    if not title_valid or not labels_valid:
        comment_message = "Pull Request validation failed:\n"
        if not title_valid:
            comment_message += f"- {title_msg}\n"
        if not labels_valid:
            comment_message += f"- {labels_msg}\n"
        post_comment(repo, pr_number, comment_message, token)
        print(comment_message)
        sys.exit(1)

    print('PR validation passed')
    sys.exit(0)

if __name__ == '__main__':
    main()