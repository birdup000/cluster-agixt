from flask import Flask, render_template, request, jsonify
from agixtsdk import AGiXTSDK
from cluster_coordinator import ClusterCoordinator
import math
import time

app = Flask(__name__)

# Initialize the ClusterCoordinator
base_uri = "http://localhost:7437"
api_key = "your_api_key"
nodes = ["node1", "node2", "node3", "node4"]
coordinator = ClusterCoordinator(base_uri, api_key, nodes)

@app.route('/')
def index():
    return render_template('index.html', nodes=nodes)

@app.route('/execute_task', methods=['POST'])
def execute_task():
    task_function = eval(request.form['task_function'])
    task_args = eval(request.form['task_args'])
    
    start_time = time.time()
    result = coordinator.execute_task(task_function, *task_args)
    end_time = time.time()
    
    return jsonify({
        'result': result,
        'execution_time': end_time - start_time
    })

@app.route('/get_task_status')
def get_task_status():
    return jsonify({
        'node_tasks': coordinator.subtask_assignments,
        'node_agents': {node: agent['agent_name'] for node, agent in coordinator.task_execution_agents.items()}
    })

if __name__ == '__main__':
    app.run(debug=True)