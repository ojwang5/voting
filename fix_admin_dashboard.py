with open('templates/polls/admin_dashboard.html', 'r') as f:
    content = f.read()

# The exact block to replace
old = '''                        <div class="row g-3">
                            <div class="col-md-3">
                                <a href="{% url 'polls:create_election' %}" class="btn btn-success w-100 py-3">
                                    <i class="bi bi-plus-circle d-block fs-4 mb-2"></i>
                                    Create Election
                                </a>
                            </div>
                            <div class="col-md-3">
                                <a href="{% url 'polls:admin_register_candidate' %}" class="btn btn-info w-100 py-3">
                                    <i class="bi bi-person-plus d-block fs-4 mb-2"></i>
                                    Register Candidate
                                </a>
                            </div>
                            <div class="col-md-3">
                                <a href="{% url 'polls:admin_register_voter' %}" class="btn btn-warning w-100 py-3">
                                    <i class="bi bi-shield-plus d-block fs-4 mb-2"></i>
                                    Register Voter
                                </a>
                            </div>
                            <div class="col-md-3">
                                <a href="/admin/" class="btn btn-secondary w-100 py-3">
                                    <i class="bi bi-gear-wide-connected d-block fs-4 mb-2"></i>
                                    Super Admin
                                </a>
                            </div>'''

new = '''                        <div class="row g-3">
                            {% if is_superadmin %}
                            <div class="col-md-3">
                                <a href="{% url 'polls:create_election' %}" class="btn btn-success w-100 py-3">
                                    <i class="bi bi-plus-circle d-block fs-4 mb-2"></i>
                                    Create Election
                                </a>
                            </div>
                            <div class="col-md-3">
                                <a href="{% url 'polls:admin_register_candidate' %}" class="btn btn-info w-100 py-3">
                                    <i class="bi bi-person-plus d-block fs-4 mb-2"></i>
                                    Register Candidate
                                </a>
                            </div>
                            {% endif %}
                            <div class="col-md-3">
                                <a href="{% url 'polls:admin_register_voter' %}" class="btn btn-warning w-100 py-3">
                                    <i class="bi bi-shield-plus d-block fs-4 mb-2"></i>
                                    Register Voter
                                </a>
                            </div>
                            <div class="col-md-3">
                                <a href="{% url 'polls:bulk_register_voters' %}" class="btn btn-outline-warning w-100 py-3">
                                    <i class="bi bi-upload d-block fs-4 mb-2"></i>
                                    Bulk Upload
                                </a>
                            </div>
                            {% if is_superadmin %}
                            <div class="col-md-3">
                                <a href="/admin/" class="btn btn-secondary w-100 py-3">
                                    <i class="bi bi-gear-wide-connected d-block fs-4 mb-2"></i>
                                    Super Admin
                                </a>
                            </div>
                            {% endif %}
                        </div>'''

if old in content:
    content = content.replace(old, new)
    with open('templates/polls/admin_dashboard.html', 'w') as f:
        f.write(content)
    print('admin_dashboard.html updated successfully!')
else:
    print('Pattern not found!')
