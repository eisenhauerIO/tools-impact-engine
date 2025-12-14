# Implementation Plan

- [x] 1. Set up modeling layer structure and dependencies
  - Create `impact_engine/modeling/` directory structure
  - Add statsmodels dependency to pyproject.toml
  - Create `__init__.py` files for proper package structure
  - _Requirements: 1.1, 2.1_

- [ ] 2. Implement core modeling interfaces
  - [x] 2.1 Create ModelInterface abstract base class
    - Define abstract methods: fit
    - Include proper type hints and docstrings
    - _Requirements: 2.1_

  - [ ]* 2.2 Write property test for interface consistency
    - **Property 3: Interface consistency**
    - **Validates: Requirements 2.1**

  - [x] 2.3 Create ModelingEngine manager class
    - Implement model registration system
    - Add method to get and fit models
    - _Requirements: 2.1, 2.3_

  - [ ]* 2.4 Write property test for data format compatibility
    - **Property 4: Data format compatibility**
    - **Validates: Requirements 2.3**

- [ ] 3. Implement interrupted time series model
  - [x] 3.1 Create InterruptedTimeSeriesModel class
    - Implement ModelInterface fit method
    - Use SARIMAX for time series modeling with intervention dummy variables
    - _Requirements: 1.1_

  - [ ]* 3.2 Write property test for model fitting completeness
    - **Property 1: Model fitting completeness**
    - **Validates: Requirements 1.1**

- [ ] 4. Implement result saving and output formatting
  - [x] 4.1 Create result file saving functionality
    - Save impact estimates to JSON format
    - Return file path to saved results
    - _Requirements: 1.2, 1.3_

  - [ ]* 4.2 Write property test for output file consistency
    - **Property 2: Output file consistency**
    - **Validates: Requirements 1.2, 1.3, 2.2**

- [ ] 5. Integrate with existing impact analysis workflow
  - [x] 5.1 Update evaluate_impact function
    - Add modeling layer integration after data retrieval
    - Pass business metrics to modeling engine
    - _Requirements: 2.3_

  - [x] 5.2 Write integration tests
    - Test end-to-end workflow from data retrieval to model results
    - Test with simulated data from existing system
    - _Requirements: 1.1, 2.3_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.