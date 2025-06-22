class RWAApp {
    constructor() {
        this.baseURL = window.location.origin;
        this.currentWallet = null;
        this.currentAssets = [];
        this.currentAsset = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadSampleWallet();
    }

    setupEventListeners() {
        // Asset form submission
        document.getElementById('asset-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitAsset();
        });

        // Refresh assets button
        document.getElementById('refresh-assets').addEventListener('click', () => {
            this.loadUserAssets();
        });

        // Modal action buttons
        document.getElementById('verify-btn').addEventListener('click', () => {
            this.verifyAsset();
        });

        document.getElementById('tokenize-btn').addEventListener('click', () => {
            this.tokenizeAsset();
        });
    }

    loadSampleWallet() {
        // Load a sample wallet for demo purposes
        const sampleWallet = '0x742d35Cc6e34d8d7C15fE14c123456789abcdef0';
        document.getElementById('wallet-address').value = sampleWallet;
        this.currentWallet = sampleWallet;
        document.getElementById('wallet-display').textContent = `${sampleWallet.substr(0, 6)}...${sampleWallet.substr(-4)}`;
        this.loadUserAssets();
    }

    async submitAsset() {
        const submitBtn = document.getElementById('submit-btn');
        const spinner = document.getElementById('submit-spinner');
        
        try {
            this.setLoading(submitBtn, spinner, true);
            
            const walletAddress = document.getElementById('wallet-address').value;
            const assetDescription = document.getElementById('asset-description').value;
            const email = document.getElementById('email').value;

            const response = await fetch(`${this.baseURL}/api/intake`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    wallet_address: walletAddress,
                    user_input: assetDescription,
                    email: email
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', 'Asset submitted successfully!');
                this.showFollowUpQuestions(result.follow_up_questions);
                this.resetForm();
                this.loadUserAssets();
                this.loadStats();
            } else {
                this.showAlert('danger', `Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error submitting asset:', error);
            this.showAlert('danger', 'Failed to submit asset. Please try again.');
        } finally {
            this.setLoading(submitBtn, spinner, false);
        }
    }

    async loadUserAssets() {
        const walletAddress = document.getElementById('wallet-address').value;
        if (!walletAddress) return;

        try {
            const response = await fetch(`${this.baseURL}/api/assets/${walletAddress}`);
            const result = await response.json();
            
            this.currentAssets = result.assets || [];
            this.renderAssets(this.currentAssets);
        } catch (error) {
            console.error('Error loading assets:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/stats`);
            const stats = await response.json();
            
            document.getElementById('total-assets').textContent = stats.total_assets || 0;
            document.getElementById('verified-assets').textContent = stats.verified_assets || 0;
            document.getElementById('tokenized-assets').textContent = stats.tokenized_assets || 0;
            document.getElementById('total-users').textContent = stats.total_users || 0;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderAssets(assets) {
        const assetsList = document.getElementById('assets-list');
        
        if (assets.length === 0) {
            assetsList.innerHTML = `
                <div class="text-center text-muted">
                    <p>No assets found. Submit your first asset above!</p>
                </div>
            `;
            return;
        }

        assetsList.innerHTML = assets.map(asset => `
            <div class="card mb-2">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="card-title">${this.getAssetTypeIcon(asset.asset_type)} ${asset.asset_type.replace('_', ' ').toUpperCase()}</h6>
                            <p class="card-text small">${asset.description.substring(0, 80)}...</p>
                            <div class="d-flex gap-2">
                                <span class="badge bg-secondary">${asset.estimated_value?.toLocaleString() || 'N/A'} ${asset.currency || ''}</span>

                                ${asset.token_id ? '<span class="badge bg-success">Tokenized</span>' : ''}
                            </div>
                        </div>
                        <button class="btn btn-outline-primary btn-sm" onclick="app.showAssetDetails(${asset.id})">
                            View
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async showAssetDetails(assetId) {
        try {
            const response = await fetch(`${this.baseURL}/api/asset/${assetId}`);
            const result = await response.json();
            const asset = result.asset;
            const transactions = result.transactions || [];

            // Store current asset for modal actions
            this.currentAsset = asset;

            // Populate modal
            document.getElementById('asset-modal-body').innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Asset Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Type:</strong></td><td>${asset.asset_type.replace('_', ' ')}</td></tr>
                            <tr><td><strong>Value:</strong></td><td>${asset.estimated_value?.toLocaleString() || 'N/A'} ${asset.currency || ''}</td></tr>

                            <tr><td><strong>Location:</strong></td><td>${asset.location}</td></tr>
                            <tr><td><strong>Status:</strong></td><td><span class="badge bg-${this.getStatusColor(asset.verification_status)}">${asset.verification_status}</span></td></tr>
                            <tr><td><strong>Created:</strong></td><td>${new Date(asset.created_at).toLocaleDateString()}</td></tr>
                            ${asset.token_id ? `<tr><td><strong>Token ID:</strong></td><td><code>${asset.token_id}</code></td></tr>` : ''}
                        </table>
                        <h6>Description</h6>
                        <p class="small">${asset.description}</p>
                    </div>
                    <div class="col-md-6">
                        <h6>Transaction History</h6>
                        ${transactions.length > 0 ? `
                            <div class="list-group">
                                ${transactions.map(tx => `
                                    <div class="list-group-item">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h6 class="mb-1">${tx.transaction_type}</h6>
                                            <small>${new Date(tx.created_at).toLocaleDateString()}</small>
                                        </div>
                                        <p class="mb-1"><span class="badge bg-${this.getStatusColor(tx.status)}">${tx.status}</span></p>
                                        ${tx.transaction_hash ? `<small>Hash: <code>${tx.transaction_hash.substr(0, 16)}...</code></small>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p class="text-muted">No transactions yet</p>'}
                    </div>
                </div>
            `;

            // Show appropriate action buttons
            document.getElementById('verify-btn').classList.toggle('d-none', asset.verification_status !== 'pending');
            document.getElementById('tokenize-btn').classList.toggle('d-none', asset.verification_status !== 'verified');

            // Show modal
            new bootstrap.Modal(document.getElementById('asset-modal')).show();

        } catch (error) {
            console.error('Error loading asset details:', error);
            this.showAlert('danger', 'Failed to load asset details');
        }
    }

    async verifyAsset() {
        if (!this.currentAsset) return;

        try {
            const response = await fetch(`${this.baseURL}/api/verify/${this.currentAsset.id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', 'Asset verification completed!');
                this.loadUserAssets();
                this.loadStats();
                
                // Close modal and show results
                bootstrap.Modal.getInstance(document.getElementById('asset-modal')).hide();
                
                // Show verification details
                this.showVerificationResults(result.verification_result);
            } else {
                this.showAlert('danger', `Verification failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Error verifying asset:', error);
            this.showAlert('danger', 'Failed to verify asset');
        }
    }

    async tokenizeAsset() {
        if (!this.currentAsset) return;

        try {
            const response = await fetch(`${this.baseURL}/api/tokenize/${this.currentAsset.id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', 'Asset tokenized successfully!');
                this.loadUserAssets();
                this.loadStats();
                
                // Close modal and show results
                bootstrap.Modal.getInstance(document.getElementById('asset-modal')).hide();
                
                // Show tokenization details
                this.showTokenizationResults(result.tokenization_result);
            } else {
                this.showAlert('danger', `Tokenization failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Error tokenizing asset:', error);
            this.showAlert('danger', 'Failed to tokenize asset');
        }
    }

    showVerificationResults(verificationResult) {
        const alertHtml = `
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                <h6>🔍 Verification Results</h6>
                <p><strong>Overall Score:</strong> ${(verificationResult.overall_score * 100).toFixed(1)}%</p>
                <p><strong>Status:</strong> <span class="badge bg-${this.getStatusColor(verificationResult.status)}">${verificationResult.status}</span></p>
                ${verificationResult.recommendations.length > 0 ? `
                    <p><strong>Recommendations:</strong></p>
                    <ul>${verificationResult.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
                ` : ''}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').innerHTML = alertHtml;
    }

    showTokenizationResults(tokenizationResult) {
        const alertHtml = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <h6>🎉 Tokenization Successful!</h6>
                <p><strong>Token ID:</strong> <code>${tokenizationResult.token_id}</code></p>
                <p><strong>Contract:</strong> <code>${tokenizationResult.contract_address}</code></p>
                <p><strong>Transaction:</strong> <code>${tokenizationResult.transaction_hash}</code></p>
                <p><strong>Network:</strong> ${tokenizationResult.network}</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').innerHTML = alertHtml;
    }

    showFollowUpQuestions(questions) {
        if (questions.length === 0) return;

        const questionsHtml = questions.map(question => `
            <div class="alert alert-info mb-2">
                <small><strong>💭 ${question}</strong></small>
            </div>
        `).join('');

        document.getElementById('follow-up-questions').innerHTML = questionsHtml;
        document.getElementById('follow-up-section').classList.remove('d-none');

        // Hide after 10 seconds
        setTimeout(() => {
            document.getElementById('follow-up-section').classList.add('d-none');
        }, 10000);
    }

    showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').innerHTML = alertHtml;

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alertElement = document.querySelector('.alert');
            if (alertElement) {
                const alert = new bootstrap.Alert(alertElement);
                alert.close();
            }
        }, 5000);
    }

    resetForm() {
        document.getElementById('asset-description').value = '';
        document.getElementById('email').value = '';
    }

    setLoading(button, spinner, isLoading) {
        if (isLoading) {
            button.disabled = true;
            spinner.classList.remove('d-none');
            button.textContent = 'Processing...';
        } else {
            button.disabled = false;
            spinner.classList.add('d-none');
            button.textContent = 'Submit Asset';
        }
    }

    getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'verified': 'success',
            'rejected': 'danger',
            'requires_review': 'info',
            'completed': 'success',
            'failed': 'danger'
        };
        return colors[status] || 'secondary';
    }

    getAssetTypeIcon(assetType) {
        const icons = {
            'real_estate': '🏠',
            'vehicle': '🚗',
            'artwork': '🎨',
            'equipment': '⚙️',
            'commodity': '📦',
            'unknown': '❓'
        };
        return icons[assetType] || '📄';
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new RWAApp();
});