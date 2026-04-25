import re

# Fix admin_dashboard.html
with open('templates/polls/admin_dashboard.html', 'r') as f:
    content = f.read()

old = '''                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-lightning me-2 text-success"></i>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
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
                            </div>
                    </div>'''

new = '''                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-lightning me-2 text-success"></i>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-3">
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
                            {% if is_superadmin %}
                            <div class="col-md-3">
                                <a href="/admin/" class="btn btn-secondary w-100 py-3">
                                    <i class="bi bi-gear-wide-connected d-block fs-4 mb-2"></i>
                                    Super Admin
                                </a>
                            </div>
                            {% endif %}
                        </div>'''

content = content.replace(old, new)

with open('templates/polls/admin_dashboard.html', 'w') as f:
    f.write(content)

print('admin_dashboard.html updated!')

# Fix admin_elections.html
with open('templates/polls/admin_elections.html', 'r') as f:
    content = f.read()

# Hide Create Election button for ADMIN
old = '''            <div>
                <a href="{% url 'polls:create_election' %}" class="btn btn-success me-2">
                    <i class="bi bi-plus-circle"></i> Create Election
                </a>
                <a href="{% url 'polls:admin_dashboard' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Dashboard
                </a>
            </div>'''

new = '''            <div>
                {% if is_superadmin %}
                <a href="{% url 'polls:create_election' %}" class="btn btn-success me-2">
                    <i class="bi bi-plus-circle"></i> Create Election
                </a>
                {% endif %}
                <a href="{% url 'polls:admin_dashboard' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Dashboard
                </a>
            </div>'''

content = content.replace(old, new)

# Hide Edit button for ADMIN
old = '''                                        <div class="btn-group btn-group-sm">
                                            <a href="{% url 'polls:edit_election' election.id %}" class="btn btn-outline-primary" title="Edit">
                                                <i class="bi bi-pencil"></i> Edit
                                            </a>
                                            <a href="{% url 'polls:results' election.id %}" class="btn btn-outline-success" title="View Results">
                                                <i class="bi bi-bar-chart"></i>
                                            </a>'''

new = '''                                        <div class="btn-group btn-group-sm">
                                            {% if is_superadmin %}
                                            <a href="{% url 'polls:edit_election' election.id %}" class="btn btn-outline-primary" title="Edit">
                                                <i class="bi bi-pencil"></i> Edit
                                            </a>
                                            {% endif %}
                                            <a href="{% url 'polls:results' election.id %}" class="btn btn-outline-success" title="View Results">
                                                <i class="bi bi-bar-chart"></i>
                                            </a>'''

content = content.replace(old, new)

with open('templates/polls/admin_elections.html', 'w') as f:
    f.write(content)

print('admin_elections.html updated!')

# Fix admin_candidates.html
with open('templates/polls/admin_candidates.html', 'r') as f:
    content = f.read()

# Hide Add Candidate button for ADMIN
old = '''            <div>
                <a href="{% url 'polls:admin_register_candidate' %}" class="btn btn-info me-2">
                    <i class="bi bi-plus-circle"></i> Add Candidate
                </a>
                <a href="{% url 'polls:admin_dashboard' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Dashboard
                </a>
            </div>'''

new = '''            <div>
                {% if is_superadmin %}
                <a href="{% url 'polls:admin_register_candidate' %}" class="btn btn-info me-2">
                    <i class="bi bi-plus-circle"></i> Add Candidate
                </a>
                {% endif %}
                <a href="{% url 'polls:admin_dashboard' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Dashboard
                </a>
            </div>'''

content = content.replace(old, new)

# Hide Edit/Delete buttons for ADMIN
old = '''                                        <div class="btn-group btn-group-sm">
                                            <a href="{% url 'polls:view_candidate' candidate.id %}" class="btn btn-outline-info" title="View">
                                                <i class="bi bi-eye"></i>
                                            </a>
                                            <a href="{% url 'polls:admin_edit_candidate' candidate.id %}" class="btn btn-outline-primary" title="Edit">
                                                <i class="bi bi-pencil"></i>
                                            </a>
                                            <a href="{% url 'polls:admin_delete_candidate' candidate.id %}" class="btn btn-outline-danger" title="Delete" onclick="return confirm('Delete {{ candidate.name }}?')">
                                                <i class="bi bi-trash"></i>
                                            </a>
                                        </div>'''

new = '''                                        <div class="btn-group btn-group-sm">
                                            <a href="{% url 'polls:view_candidate' candidate.id %}" class="btn btn-outline-info" title="View">
                                                <i class="bi bi-eye"></i>
                                            </a>
                                            {% if is_superadmin %}
                                            <a href="{% url 'polls:admin_edit_candidate' candidate.id %}" class="btn btn-outline-primary" title="Edit">
                                                <i class="bi bi-pencil"></i>
                                            </a>
                                            <a href="{% url 'polls:admin_delete_candidate' candidate.id %}" class="btn btn-outline-danger" title="Delete" onclick="return confirm('Delete {{ candidate.name }}?')">
                                                <i class="bi bi-trash"></i>
                                            </a>
                                            {% endif %}
                                        </div>'''

content = content.replace(old, new)

with open('templates/polls/admin_candidates.html', 'w') as f:
    f.write(content)

print('admin_candidates.html updated!')

# Fix admin_positions.html
with open('templates/polls/admin_positions.html', 'r') as f:
    content = f.read()

# Hide Add Position form for ADMIN
old = '''        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="bi bi-plus-circle me-2"></i>Add New Position</h5>
            </div>
            <div class="card-body">
                <form method="post" class="row g-3">
                    {% csrf_token %}
                    <div class="col-md-8">
                        <input type="text" name="name" class="form-control" 
                               placeholder="Position name (e.g., President, Vice President, Secretary General)" 
                               required maxlength="100">
                    </div>
                    <div class="col-md-4">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-check-lg"></i> Add Position
                        </button>
                    </div>
                </form>
            </div>'''

new = '''        {% if is_superadmin %}
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="bi bi-plus-circle me-2"></i>Add New Position</h5>
            </div>
            <div class="card-body">
                <form method="post" class="row g-3">
                    {% csrf_token %}
                    <div class="col-md-8">
                        <input type="text" name="name" class="form-control" 
                               placeholder="Position name (e.g., President, Vice President, Secretary General)" 
                               required maxlength="100">
                    </div>
                    <div class="col-md-4">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-check-lg"></i> Add Position
                        </button>
                    </div>
                </form>
            </div>
        {% endif %}'''

content = content.replace(old, new)

# Hide Edit/Delete buttons for ADMIN
old = '''                                    <td>
                                        <a href="{% url 'polls:admin_position_edit' position.id %}" class="btn btn-sm btn-outline-primary">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        {% if position.election_set.count == 0 and position.candidate_set.count == 0 %}
                                            <a href="{% url 'polls:admin_position_delete' position.id %}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Delete this position?')">
                                                <i class="bi bi-trash"></i>
                                            </a>
                                        {% endif %}
                                    </td>'''

new = '''                                    <td>
                                        {% if is_superadmin %}
                                        <a href="{% url 'polls:admin_position_edit' position.id %}" class="btn btn-sm btn-outline-primary">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        {% if position.election_set.count == 0 and position.candidate_set.count == 0 %}
                                            <a href="{% url 'polls:admin_position_delete' position.id %}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Delete this position?')">
                                                <i class="bi bi-trash"></i>
                                            </a>
                                        {% endif %}
                                        {% endif %}
                                    </td>'''

content = content.replace(old, new)

with open('templates/polls/admin_positions.html', 'w') as f:
    f.write(content)

print('admin_positions.html updated!')

# Fix admin_voters.html - add bulk upload button
with open('templates/polls/admin_voters.html', 'r') as f:
    content = f.read()

old = '''            <div>
                <a href="{% url 'polls:admin_register_voter' %}" class="btn btn-warning me-2">
                    <i class="bi bi-plus-circle"></i> Register Voter
                </a>
                <a href="{% url 'polls:admin_dashboard' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Dashboard
                </a>
            </div>'''

new = '''            <div>
                <a href="{% url 'polls:admin_register_voter' %}" class="btn btn-warning me-2">
                    <i class="bi bi-plus-circle"></i> Register Voter
                </a>
                <a href="{% url 'polls:bulk_register_voters' %}" class="btn btn-outline-warning me-2">
                    <i class="bi bi-upload"></i> Bulk Upload
                </a>
                <a href="{% url 'polls:admin_dashboard' %}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Dashboard
                </a>
            </div>'''

content = content.replace(old, new)

with open('templates/polls/admin_voters.html', 'w') as f:
    f.write(content)

print('admin_voters.html updated!')

print('All admin templates updated successfully!')
